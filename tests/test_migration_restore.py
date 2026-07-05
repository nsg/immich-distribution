import hashlib
import os
from pathlib import Path
import time

import httpx
import pytest


IMMICH_URL = os.environ.get("IMMICH_URL", "http://localhost:2283").rstrip("/")
BACKUP_FILE_ENV = os.environ.get("BACKUP_FILE", "")
BACKUP_FILE = Path(BACKUP_FILE_ENV)
API_KEY = os.environ.get("API_KEY", "")
ASSET_DIR = Path(os.environ.get("ASSET_DIR", "assets"))


def log(message: str) -> None:
    print(message, flush=True)


def wait_for(description: str, check, *, timeout: float = 300, interval: float = 5):
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except Exception as error:
            last_error = error

        time.sleep(interval)

    if last_error is not None:
        raise AssertionError(f"timed out waiting for {description}") from last_error

    raise AssertionError(f"timed out waiting for {description}")


def server_ping(client: httpx.Client) -> bool:
    response = client.get(f"{IMMICH_URL}/api/server/ping")
    return response.is_success and response.json().get("res") == "pong"


def start_restore_flow(session: httpx.Client) -> None:
    log("Start restore flow")
    response = session.post(f"{IMMICH_URL}/api/admin/database-backups/start-restore")
    assert response.status_code in (200, 201), response.text


def wait_for_maintenance_mode(session: httpx.Client) -> None:
    log("Wait for maintenance mode")

    def in_maintenance() -> bool:
        response = session.get(f"{IMMICH_URL}/api/admin/maintenance/status")
        return response.is_success and response.json().get("active") is True

    wait_for("maintenance mode", in_maintenance)


def login_with_maintenance_token(session: httpx.Client) -> None:
    log("Login with maintenance token")
    response = session.post(f"{IMMICH_URL}/api/admin/maintenance/login", json={})
    assert response.status_code in (200, 201), response.text


def upload_backup(session: httpx.Client) -> str:
    log(f"Upload backup file: {BACKUP_FILE}")
    with BACKUP_FILE.open("rb") as backup:
        response = session.post(
            f"{IMMICH_URL}/api/admin/database-backups/upload",
            files={"file": (BACKUP_FILE.name, backup)},
        )
    assert response.status_code in (200, 201), response.text

    response = session.get(f"{IMMICH_URL}/api/admin/database-backups")
    response.raise_for_status()

    backups = response.json().get("backups", [])
    uploaded = [backup["filename"] for backup in backups if backup["filename"].startswith("uploaded-")]
    assert uploaded, f"no uploaded backup found in listing: {backups}"

    filename = uploaded[0]
    log(f"Found uploaded backup: {filename}")
    return filename


def trigger_restore(session: httpx.Client, backup_filename: str) -> None:
    log("Trigger database restore")
    response = session.post(
        f"{IMMICH_URL}/api/admin/maintenance",
        json={"action": "restore_database", "restoreBackupFilename": backup_filename},
    )
    assert response.status_code in (200, 201), response.text


def wait_for_restore_to_finish(session: httpx.Client) -> None:
    log("Poll restore progress")

    # A single connection error can be a transient blip while the restore
    # is still running, so only treat repeated errors as the server
    # restarting out of maintenance mode.
    consecutive_errors = 0

    for _ in range(120):
        try:
            response = session.get(f"{IMMICH_URL}/api/admin/maintenance/status")
            status = response.json()
        except (httpx.HTTPError, ValueError):
            consecutive_errors += 1
            log("Status endpoint unavailable, server may be restarting after restore")
            if consecutive_errors >= 3:
                return
            time.sleep(5)
            continue

        consecutive_errors = 0

        if status.get("error"):
            raise AssertionError(f"restore failed: {status['error']}")

        log(f"Restore progress: task={status.get('task', '')} progress={status.get('progress', '')}")

        if status.get("active") is False:
            log("Maintenance mode ended")
            return

        time.sleep(5)

    raise AssertionError("restore did not finish within timeout")


def assert_api_key_authenticates(client: httpx.Client) -> dict:
    log("Verify migrated API key authentication")

    # The server may still be settling right after the post-restore
    # restart, so retry until the key authenticates.
    def authenticated() -> dict | None:
        response = client.get(f"{IMMICH_URL}/api/users/me", headers={"X-API-KEY": API_KEY})
        return response.json() if response.status_code == 200 else None

    user = wait_for("API key authentication", authenticated, timeout=120)
    log(f"Authenticated as: {user.get('email', 'unknown')}")
    return user


def assert_assets_exist(client: httpx.Client, headers: dict[str, str]) -> list[dict]:
    log("Verify restored assets exist")
    response = client.post(f"{IMMICH_URL}/api/search/metadata", headers=headers, json={})
    assert response.status_code == 200, response.text

    items = response.json().get("assets", {}).get("items", [])
    log(f"Asset count: {len(items)}")
    assert items
    return items


def assert_asset_file_integrity(client: httpx.Client, headers: dict[str, str], filename: str) -> None:
    local_path = ASSET_DIR / filename
    assert local_path.is_file(), f"local asset for hash check not found: {local_path}"

    log(f"Verify asset file integrity for {filename}")
    local_hash = hashlib.sha256(local_path.read_bytes()).hexdigest()

    response = client.post(
        f"{IMMICH_URL}/api/search/metadata",
        headers=headers,
        json={"originalFileName": filename},
    )
    assert response.status_code == 200, response.text

    items = response.json().get("assets", {}).get("items", [])
    assert len(items) == 1, f"expected 1 result for {filename}, got {len(items)}"

    response = client.get(f"{IMMICH_URL}/api/assets/{items[0]['id']}/original", headers=headers)
    assert response.status_code == 200, response.text

    remote_hash = hashlib.sha256(response.content).hexdigest()
    log(f"Local hash:  {local_hash}")
    log(f"Remote hash: {remote_hash}")
    assert local_hash == remote_hash


def log_smart_search_status(client: httpx.Client, headers: dict[str, str]) -> None:
    log("Verify smart search status")
    response = client.post(f"{IMMICH_URL}/api/search/smart", headers=headers, json={"query": "person"})
    if response.status_code != 200:
        log(f"Smart search failed with HTTP {response.status_code}: {response.text}")
        return

    items = response.json().get("assets", {}).get("items", [])
    log(f"Smart search for 'person' returned {len(items)} results")


@pytest.mark.migration
@pytest.mark.timeout(1200)
def test_builtin_backup_restores_through_onboarding_flow() -> None:
    assert API_KEY, "API_KEY not set"
    assert BACKUP_FILE_ENV, "BACKUP_FILE not set"
    assert BACKUP_FILE.is_file(), f"backup file not found: {BACKUP_FILE}"

    log(f"Use Immich URL: {IMMICH_URL}")
    log(f"Use backup: {BACKUP_FILE}")

    with httpx.Client(timeout=30.0, trust_env=False) as session:
        log("Wait for server ping")
        wait_for("server ping", lambda: server_ping(session))

        start_restore_flow(session)
        wait_for_maintenance_mode(session)
        login_with_maintenance_token(session)
        backup_filename = upload_backup(session)
        trigger_restore(session, backup_filename)
        wait_for_restore_to_finish(session)

    with httpx.Client(timeout=30.0, trust_env=False) as client:
        log("Wait for server ping after restore")
        wait_for("server ping after restore", lambda: server_ping(client))

        assert_api_key_authenticates(client)
        headers = {"X-API-KEY": API_KEY, "Accept": "application/json"}
        assert_assets_exist(client, headers)
        assert_asset_file_integrity(client, headers, "field.jpg")
        log_smart_search_status(client, headers)

    log("Migration restore test completed successfully")
