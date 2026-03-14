"""
Test that a snap's built-in Immich backup (.sql.gz) can be restored into
upstream Docker Immich using the official onboarding restore flow.

Expects env vars:
  BACKUP_FILE: path to .sql.gz backup
  API_KEY: snap API key to verify after restore
  IMMICH_URL: base URL (default http://localhost:2283)
"""

import os
import sys
import time

import requests

IMMICH_URL = os.environ.get("IMMICH_URL", "http://localhost:2283")
BACKUP_FILE = os.environ.get("BACKUP_FILE", "")
API_KEY = os.environ.get("API_KEY", "")


def log(msg):
    print(f"DOCKER RESTORE TEST: {msg}", flush=True)


def die(msg):
    print(f"DOCKER RESTORE TEST FAILED: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def wait_for(description, check_fn, attempts=60, interval=5):
    for i in range(attempts):
        try:
            if check_fn():
                return
        except Exception:
            pass
        if i == attempts - 1:
            die(f"Timed out waiting for: {description}")
        time.sleep(interval)


def ping():
    r = requests.get(f"{IMMICH_URL}/api/server/ping", timeout=5)
    return r.ok and r.json().get("res") == "pong"


def main():
    if not BACKUP_FILE:
        die("BACKUP_FILE not set")
    if not API_KEY:
        die("API_KEY not set")
    if not os.path.isfile(BACKUP_FILE):
        die(f"Backup file not found: {BACKUP_FILE}")

    log(f"Using backup: {BACKUP_FILE}")
    session = requests.Session()

    # Wait for server to be ready (onboarding mode, no admin yet)
    log("Waiting for server to start...")
    wait_for("server ping", ping)

    # Step 1: Start restore flow
    log("Starting restore flow...")
    r = session.post(f"{IMMICH_URL}/admin/database-backups/start-restore")
    if r.status_code not in (200, 201):
        die(f"start-restore failed (HTTP {r.status_code}): {r.text}")

    # Step 2: Wait for maintenance mode
    log("Waiting for maintenance mode...")
    time.sleep(5)

    def in_maintenance():
        r = session.get(f"{IMMICH_URL}/admin/maintenance/status", timeout=5)
        return r.ok and r.json().get("active") is True

    wait_for("maintenance mode", in_maintenance)

    # Step 3: Login with maintenance token
    log("Logging in with maintenance token...")
    r = session.post(
        f"{IMMICH_URL}/admin/maintenance/login",
        json={},
    )
    if r.status_code not in (200, 201):
        die(f"maintenance login failed (HTTP {r.status_code}): {r.text}")

    # Step 4: Upload backup file
    log("Uploading backup file...")
    with open(BACKUP_FILE, "rb") as f:
        r = session.post(
            f"{IMMICH_URL}/admin/database-backups/upload",
            files={"file": (os.path.basename(BACKUP_FILE), f)},
        )
    if r.status_code not in (200, 201):
        die(f"backup upload failed (HTTP {r.status_code}): {r.text}")

    # Step 5: List backups to get the uploaded filename
    log("Listing backups...")
    r = session.get(f"{IMMICH_URL}/admin/database-backups")
    r.raise_for_status()
    backups = r.json().get("backups", [])
    uploaded = [b["filename"] for b in backups if b["filename"].startswith("uploaded-")]
    if not uploaded:
        die(f"No uploaded backup found in listing: {backups}")
    filename = uploaded[0]
    log(f"Found uploaded backup: {filename}")

    # Step 6: Trigger restore
    log("Triggering database restore...")
    r = session.post(
        f"{IMMICH_URL}/admin/maintenance",
        json={"action": "restore_database", "restoreBackupFilename": filename},
    )
    if r.status_code not in (200, 201):
        die(f"restore trigger failed (HTTP {r.status_code}): {r.text}")

    # Step 7: Poll restore status
    log("Polling restore progress...")
    for _ in range(120):
        try:
            r = session.get(f"{IMMICH_URL}/admin/maintenance/status", timeout=5)
            status = r.json()
        except Exception:
            log("Connection lost, server is restarting after restore...")
            break

        if status.get("error"):
            die(f"Restore failed: {status['error']}")

        task = status.get("task", "")
        progress = status.get("progress", "")
        log(f"Progress: task={task} progress={progress}")

        if status.get("active") is False:
            log("Maintenance mode ended")
            break

        time.sleep(5)

    # Step 8: Wait for server to come back in normal mode
    log("Waiting for server to restart in normal mode...")
    time.sleep(10)
    wait_for("server ping after restore", ping)

    # Step 9: Verify snap API key works
    log("Verifying snap API key works in Docker Immich...")
    r = requests.get(
        f"{IMMICH_URL}/api/users/me",
        headers={"X-API-KEY": API_KEY},
    )
    if r.status_code != 200:
        die(f"Failed to authenticate with snap API key (HTTP {r.status_code}): {r.text}")

    email = r.json().get("email", "unknown")
    log(f"Authenticated as: {email}")

    log("Docker restore test completed successfully!")


if __name__ == "__main__":
    main()
