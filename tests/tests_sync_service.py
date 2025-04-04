import pytest
import subprocess
from typing import Tuple
import os
import requests
import socket
import shutil
import time

EXPECTED_INITIAL_IMAGE_COUNT = int(os.getenv("EXPECTED_INITIAL_IMAGE_COUNT", 25))

def processes_in_cgroup(unit_name: str) -> Tuple[bool, str]:
    result = subprocess.run([
        "systemd-cgls",
        "--full",
        "--no-pager",
        "-u", unit_name
        ], capture_output=True)
    
    return (result.returncode, result.stdout.decode("utf-8"))


def get_secret():
    with open("secret.txt", "r") as f:
        return f.read()


def get_headers():
    return {
        "Accept": "application/json",
        "X-API-KEY": get_secret()
    }

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_number_of_assets() -> int:
    r = requests.get(f"http://{get_ip_address()}/api/server/statistics", headers=get_headers())
    response = r.json()
    return response['photos'] + response['videos']


def get_user_id() -> str:
    r = requests.get(f"http://{get_ip_address()}/api/users/me", headers=get_headers())
    return r.json()["id"]


def get_asset_id(filename: str):
    r = requests.post(
        f"http://{get_ip_address()}/api/search/metadata",
        headers=get_headers(),
        json={"originalFileName": filename}
    )

    return r.json()['assets']['items'][0]['id']


def delete_asset(asset_id: str) -> None:
    data = { "ids": [ asset_id ] }
    r = requests.delete(f"http://{get_ip_address()}/api/assets", headers=get_headers(), json=data)
    if r.status_code not in [204]:
        raise Exception(f"Failed to delete asset {asset_id}, status code {r.status_code}. Response: {r.text}")


def sync_service_journal_messages() -> str:
    result = subprocess.run(
        ["journalctl", "--no-pager", "-n", "100", "-e", "-u", "snap.immich-distribution.sync-service.service"],
        capture_output=True
    )
    return result.stdout.decode("utf-8")


def wait_for_condition(condition_func, timeout=60, message="Waiting"):
    for _ in range(timeout):
        if condition_func():
            return True
        time.sleep(1)
    return False


@pytest.mark.skipif(os.environ["SERVICE_STATE"] != "default", reason="Skipping test")
def test_001_check_expected_state_default():
    """
    The sync service should start disabled by default, verify that it is not running
    by checking the cgroup and verify that the service is running.
    """

    rc, output = processes_in_cgroup("snap.immich-distribution.sync-service.service")

    assert rc == 0
    assert "sync-service.py" not in output
    assert get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT


@pytest.mark.skipif(os.environ["SERVICE_STATE"] != "enabled", reason="Skipping test")
def test_001_enable_sync_service():
    """
    Enable the sync service, no keys are provided so the service should not start.
    Verify that the database is modified as expected. Finally verify that the service
    exited with a non-zero exit code.
    """

    result = subprocess.run([
        "journalctl", "--no-pager", "-n", "10", "-e",
        "-u", "snap.immich-distribution.sync-service.service",
        ], capture_output=True)

    assert result.returncode == 0
    assert "CREATE TABLE" in result.stdout.decode("utf-8")
    assert "CREATE FUNCTION" in result.stdout.decode("utf-8")
    assert "CREATE TRIGGER" in result.stdout.decode("utf-8")

    result2 = subprocess.run(
        ["systemctl", "show", "snap.immich-distribution.sync-service.service", "-p", "ExecMainStatus"],
        capture_output=True
    )

    assert result2.returncode == 0
    assert "ExecMainStatus=0" in result2.stdout.decode("utf-8")


@pytest.mark.skipif(os.environ["SERVICE_STATE"] != "running", reason="Skipping test")
def test_001_running_sync_service():
    """
    Start the sync service with the correct key, verify that the service is running
    correctly by checking the cgroup and verify log output in the journal.
    """

    rc, output = processes_in_cgroup("snap.immich-distribution.sync-service.service")

    assert rc == 0
    assert "sync-service.py" in output
    assert get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT

    result = subprocess.run([
        "journalctl", "--no-pager", "-n", "10", "-e",
        "-u", "snap.immich-distribution.sync-service.service",
        ], capture_output=True)

    assert result.returncode == 0
    assert "Critical" not in result.stdout.decode("utf-8")


@pytest.mark.skipif(os.environ["SERVICE_STATE"] != "running", reason="Skipping test")
def test_010_add_file():
    """
    Add a file to the directory that the sync service is watching, verify that the
    file is added to Immich via the API.
    """

    snap_common = "/var/snap/immich-distribution/common"
    sync_file_path = os.path.join(snap_common, "sync", get_user_id(), "polemonium_reptans.jpg")
    shutil.copy("test-assets/albums/nature/polemonium_reptans.jpg", sync_file_path)

    assert wait_for_condition(
        lambda: get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT + 1,
        timeout=60,
        message="Waiting for asset to be added"
    ), sync_service_journal_messages()

@pytest.mark.skipif(os.environ["SERVICE_STATE"] != "running", reason="Skipping test")
def test_020_remove_file():
    """
    Remove a file from the directory that the sync service is watching, verify that the
    file is removed from Immich via the API.
    """

    snap_common = "/var/snap/immich-distribution/common"
    sync_file_path = os.path.join(snap_common, "sync", get_user_id(), "polemonium_reptans.jpg")
    os.remove(sync_file_path)

    assert wait_for_condition(
        lambda: get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT,
        timeout=10,
        message="Waiting for asset to be removed"
    ), sync_service_journal_messages()


@pytest.mark.skipif(os.environ["SERVICE_STATE"] != "threshold", reason="Skipping test")
def test_020_test_delete_threshold():
    """
    Add a file and test that the delete threshold is working correctly. I will do this
    by setting the delete threshold to 0 days and then remove the file.
    """

    snap_common = "/var/snap/immich-distribution/common"
    sync_file_path = os.path.join(snap_common, "sync", get_user_id(), "cyclamen_persicum.jpg")
    shutil.copy("test-assets/albums/nature/cyclamen_persicum.jpg", sync_file_path)

    assert wait_for_condition(
        lambda: get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT + 1,
        timeout=30,
        message="Waiting for asset to be added"
    ), sync_service_journal_messages()

    os.remove(sync_file_path)
    time.sleep(10)
    assert get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT + 1


@pytest.mark.skipif(os.environ["SERVICE_STATE"] != "threshold", reason="Skipping test")
def test_021_test_delete_assets_from_immich():
    """
    Add a file and delete it from Immich, verify that the file is removed.
    """

    # Verify baseline number of assets
    assert get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT + 1

    snap_common = "/var/snap/immich-distribution/common"
    sync_file_path = os.path.join(snap_common, "sync", get_user_id(), "tanners_ridge.jpg")
    shutil.copy("test-assets/albums/nature/tanners_ridge.jpg", sync_file_path)

    assert os.path.exists(sync_file_path), "File was not copied to the sync directory"

    assert wait_for_condition(
        lambda: get_number_of_assets() == EXPECTED_INITIAL_IMAGE_COUNT + 2,
        timeout=120,
        message="Waiting for asset to be added"
    ), sync_service_journal_messages()

    asset_id = get_asset_id("tanners_ridge.jpg")
    delete_asset(asset_id)
    time.sleep(30)
    requests.post(f"http://{get_ip_address()}/api/trash/empty", headers=get_headers())

    assert wait_for_condition(
        lambda: not os.path.exists(sync_file_path),
        timeout=120,
        message="Waiting for file to be removed"
    ), sync_service_journal_messages()

if __name__ == "__main__":
    pytest.main()
