import hashlib
import os
from pathlib import Path
import time

import httpx
import pytest

from helpers.command import run


IMMICH_URL = os.environ.get("IMMICH_URL", "http://localhost").rstrip("/")
API_KEY_FILE = Path(os.environ.get("API_KEY_FILE", "runtime/artifacts/api-key.txt"))
ASSET_DIR = Path(os.environ.get("ASSET_DIR", "assets"))
SNAP_BACKUP_DIR = Path("/var/snap/immich-distribution/common/backups")
DATABASE_BACKUP_ENV = os.environ.get("SNAP_DATABASE_BACKUP", "")
ASSETS_BACKUP_ENV = os.environ.get("SNAP_ASSETS_BACKUP", "")


def log(message: str) -> None:
    print(message, flush=True)


def api_key() -> str:
    assert API_KEY_FILE.is_file(), f"API key file not found: {API_KEY_FILE}"
    return API_KEY_FILE.read_text().strip()


def headers() -> dict[str, str]:
    return {"Accept": "application/json", "X-API-KEY": api_key()}


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


def find_backups(pattern: str) -> list[Path]:
    output = run(["sudo", "find", str(SNAP_BACKUP_DIR), "-name", pattern, "-type", "f"]).stdout
    return [Path(line) for line in output.splitlines() if line.strip()]


def assert_file_is_not_empty(path: Path) -> None:
    run(["sudo", "test", "-s", str(path)])


def copy_to_snap_backup_dir(path: Path) -> Path:
    destination = SNAP_BACKUP_DIR / path.name
    run(["sudo", "cp", "-v", str(path), str(destination)])
    return destination


def get_restored_asset(client: httpx.Client, filename: str) -> dict:
    response = client.post(
        f"{IMMICH_URL}/api/search/metadata",
        headers=headers(),
        json={"originalFileName": filename},
    )
    assert response.status_code == 200, response.text

    items = response.json().get("assets", {}).get("items", [])
    assert len(items) == 1, f"expected 1 result for {filename}, got {len(items)}"
    return items[0]


def assert_asset_file_integrity(client: httpx.Client, filename: str) -> None:
    local_path = ASSET_DIR / filename
    assert local_path.is_file(), f"local asset not found: {local_path}"

    log(f"Verify restored asset file integrity for {filename}")
    local_hash = hashlib.sha256(local_path.read_bytes()).hexdigest()
    asset = get_restored_asset(client, filename)

    response = client.get(f"{IMMICH_URL}/api/assets/{asset['id']}/original", headers=headers())
    assert response.status_code == 200, response.text

    remote_hash = hashlib.sha256(response.content).hexdigest()
    log(f"Local hash:  {local_hash}")
    log(f"Remote hash: {remote_hash}")
    assert local_hash == remote_hash


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_snap_backup_command_creates_database_and_asset_archives() -> None:
    log("Run legacy snap backup command")
    run(["sudo", "immich-distribution.backup", "-a", "-d"])

    database_backups = find_backups("immich_database_*.sql.xz")
    asset_backups = find_backups("immich_assets_*.tar.xz")

    assert database_backups, f"no database backups found in {SNAP_BACKUP_DIR}"
    assert asset_backups, f"no asset backups found in {SNAP_BACKUP_DIR}"

    for backup in database_backups + asset_backups:
        assert_file_is_not_empty(backup)

    latest_database_backup = max(database_backups, key=lambda path: path.name)
    log(f"Validate database backup: {latest_database_backup}")
    run(["sudo", "xzgrep", "-q", "--", "-- PostgreSQL database dump complete", str(latest_database_backup)])
    run(["sudo", "xzgrep", "-q", "--", "-- PostgreSQL database cluster dump complete", str(latest_database_backup)])


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_snap_restore_command_restores_database_and_assets() -> None:
    assert DATABASE_BACKUP_ENV, "SNAP_DATABASE_BACKUP not set"
    assert ASSETS_BACKUP_ENV, "SNAP_ASSETS_BACKUP not set"

    database_backup = Path(DATABASE_BACKUP_ENV)
    assets_backup = Path(ASSETS_BACKUP_ENV)
    assert database_backup.is_file(), f"database backup not found: {database_backup}"
    assert assets_backup.is_file(), f"assets backup not found: {assets_backup}"

    log("Copy backup artifacts into snap backup directory")
    restored_database_backup = copy_to_snap_backup_dir(database_backup)
    restored_assets_backup = copy_to_snap_backup_dir(assets_backup)

    log("Restore database through legacy snap restore command")
    run(["sudo", "immich-distribution.restore", "-y", "-d", str(restored_database_backup)])

    log("Restore assets through legacy snap restore command")
    run(["sudo", "immich-distribution.restore", "-y", "-a", str(restored_assets_backup)])

    with httpx.Client(timeout=30.0, trust_env=False) as client:
        log("Wait for restored snap API")
        wait_for("server ping after restore", lambda: server_ping(client), timeout=300, interval=5)

        log("Verify restored API key authentication")
        response = client.get(f"{IMMICH_URL}/api/users/me", headers=headers())
        assert response.status_code == 200, response.text
        assert response.json().get("isAdmin") is True

        log("Verify restored assets exist")
        response = client.post(f"{IMMICH_URL}/api/search/metadata", headers=headers(), json={})
        assert response.status_code == 200, response.text
        items = response.json().get("assets", {}).get("items", [])
        assert items

        assert_asset_file_integrity(client, "field.jpg")
