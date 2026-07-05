import os
from datetime import datetime
from pathlib import Path
import uuid

import httpx

from helpers.wait import eventually


API_KEY_FILE = Path(os.environ.get("API_KEY_FILE", "runtime/artifacts/api-key.txt"))
ASSET_DIR = Path(os.environ.get("ASSET_DIR", "assets"))
UPSTREAM_TEST_ASSET_DIR = Path(os.environ.get("UPSTREAM_TEST_ASSET_DIR", "runtime/test-assets"))

ALL_TEST_ASSETS = [
    ASSET_DIR / "ai-apple.tiff",
    ASSET_DIR / "ai-people1.png",
    ASSET_DIR / "ai-people2.png",
    ASSET_DIR / "ai-people3.png",
    ASSET_DIR / "ml-tesla1.png",
    ASSET_DIR / "ml-tesla2.png",
    ASSET_DIR / "ml-tesla3.png",
    ASSET_DIR / "ml-tesla4.png",
    ASSET_DIR / "ml-tesla5.png",
    ASSET_DIR / "ml-tesla6.png",
    ASSET_DIR / "ml-edison1.png",
    ASSET_DIR / "ml-edison2.png",
    ASSET_DIR / "ml-edison3.png",
    ASSET_DIR / "ml-edison4.png",
    ASSET_DIR / "field.jpg",
    ASSET_DIR / "grass.MP.jpg",
    ASSET_DIR / "memory.jpg",
    ASSET_DIR / "ohm.gif",
    ASSET_DIR / "plane.jpg",
    ASSET_DIR / "ship.mp4",
    ASSET_DIR / "ship-vp9.webm",
    ASSET_DIR / "PXL_20250712_111801796.jpg",
    UPSTREAM_TEST_ASSET_DIR / "formats/heic/IMG_2682.heic",
    UPSTREAM_TEST_ASSET_DIR / "formats/webp/denali.webp",
    UPSTREAM_TEST_ASSET_DIR / "formats/raw/Nikon/D80/glarus.nef",
    UPSTREAM_TEST_ASSET_DIR / "formats/raw/Nikon/D700/philadelphia.nef",
]

EXIF_TEST_ASSETS = [
    ASSET_DIR / "grass.MP.jpg",
    ASSET_DIR / "ohm.gif",
    ASSET_DIR / "ship.mp4",
    UPSTREAM_TEST_ASSET_DIR / "formats/heic/IMG_2682.heic",
]
PEOPLE_TEST_ASSETS = [
    ASSET_DIR / "ai-people1.png",
    ASSET_DIR / "ai-people2.png",
    ASSET_DIR / "ai-people3.png",
    ASSET_DIR / "ml-tesla1.png",
    ASSET_DIR / "ml-tesla2.png",
    ASSET_DIR / "ml-tesla3.png",
    ASSET_DIR / "ml-tesla4.png",
    ASSET_DIR / "ml-tesla5.png",
    ASSET_DIR / "ml-tesla6.png",
    ASSET_DIR / "ml-edison1.png",
    ASSET_DIR / "ml-edison2.png",
    ASSET_DIR / "ml-edison3.png",
    ASSET_DIR / "ml-edison4.png",
]
OCR_TEST_ASSETS = [
    ASSET_DIR / "PXL_20250712_111801796.jpg",
]


def log(message: str) -> None:
    print(message, flush=True)


def api_key() -> str:
    secret = os.environ.get("API_KEY")
    if secret:
        return secret

    assert API_KEY_FILE.is_file(), (
        f"API key file not found: {API_KEY_FILE} (run test_prep.py first to provision it)"
    )
    return API_KEY_FILE.read_text().strip()


def headers() -> dict[str, str]:
    return {"Accept": "application/json", "X-API-KEY": api_key()}


def upload_asset(client: httpx.Client, immich_url: str, path: Path) -> dict:
    stats = path.stat()
    data = {
        "deviceAssetId": f"{path}-{uuid.uuid4()}",
        "deviceId": "pytest",
        "fileCreatedAt": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "fileModifiedAt": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "isFavorite": "false",
    }

    with path.open("rb") as asset:
        response = client.post(
            f"{immich_url}/api/assets",
            headers=headers(),
            data=data,
            files={"assetData": (path.name, asset)},
        )

    assert response.status_code == 201, f"failed to upload {path}: {response.status_code} {response.text}"
    return response.json()


def upload_assets(client: httpx.Client, immich_url: str, paths: list[Path]) -> dict[str, dict]:
    assert_test_assets_exist(paths)

    uploaded = {}
    for asset_path in paths:
        log(f"Upload {asset_path}")
        response = upload_asset(client, immich_url, asset_path)
        assert response.get("id") is not None
        uploaded[asset_path.name] = response

    return uploaded


def get_asset_by_id(client: httpx.Client, immich_url: str, asset_id: str) -> dict:
    response = client.get(f"{immich_url}/api/assets/{asset_id}", headers=headers())
    assert response.status_code == 200, response.text
    return response.json()


def get_number_of_assets(client: httpx.Client, immich_url: str) -> int:
    response = client.get(f"{immich_url}/api/server/statistics", headers=headers())
    assert response.status_code == 200, response.text

    statistics = response.json()
    return statistics["photos"] + statistics["videos"]


def get_all_jobs(client: httpx.Client, immich_url: str) -> dict:
    response = client.get(f"{immich_url}/api/jobs", headers=headers())
    assert response.status_code == 200, response.text
    return response.json()


def trigger_job(client: httpx.Client, immich_url: str, job_name: str) -> None:
    response = client.put(
        f"{immich_url}/api/jobs/{job_name}",
        headers=headers(),
        json={"command": "start"},
    )
    assert response.status_code in (200, 201), response.text


def job_queue_empty(client: httpx.Client, immich_url: str) -> bool:
    # queueStatus.isActive only counts running jobs, so also count
    # waiting and delayed jobs or the queue looks empty between jobs.
    for job_data in get_all_jobs(client, immich_url).values():
        if not isinstance(job_data, dict):
            return False

        queue_status = job_data.get("queueStatus")
        if not isinstance(queue_status, dict) or queue_status.get("isPaused") or queue_status.get("isActive"):
            return False

        job_counts = job_data.get("jobCounts")
        if not isinstance(job_counts, dict):
            return False

        pending = job_counts.get("active", 0) + job_counts.get("waiting", 0) + job_counts.get("delayed", 0)
        if pending > 0:
            return False

    return True


def assert_no_failed_jobs(client: httpx.Client, immich_url: str) -> None:
    # A permanently failed job also drains the queue, so an empty queue
    # alone does not mean every asset was processed.
    failed = {}
    for name, job_data in get_all_jobs(client, immich_url).items():
        if not isinstance(job_data, dict):
            continue

        job_counts = job_data.get("jobCounts")
        if isinstance(job_counts, dict) and job_counts.get("failed", 0) > 0:
            failed[name] = job_counts["failed"]

    assert not failed, f"jobs failed during processing: {failed}"


def wait_for_empty_job_queue(client: httpx.Client, immich_url: str) -> None:
    # Queues hand off to each other, so require a few consecutive empty
    # polls to avoid declaring victory in a gap between jobs.
    consecutive_empty = 0

    def drained() -> bool:
        nonlocal consecutive_empty
        if job_queue_empty(client, immich_url):
            consecutive_empty += 1
        else:
            consecutive_empty = 0
        return consecutive_empty >= 3

    eventually(drained, timeout=600, interval=1)
    assert_no_failed_jobs(client, immich_url)


def wait_for_thumbnails(client: httpx.Client, immich_url: str, uploaded: dict[str, dict]) -> None:
    for name, asset in uploaded.items():
        log(f"Wait for thumbnail: {name}")
        eventually(
            lambda asset_id=asset["id"]: get_asset_by_id(client, immich_url, asset_id).get("thumbhash"),
            timeout=120,
            interval=2,
        )


def assert_test_assets_exist(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.is_file()]
    assert not missing, "missing test assets:\n" + "\n".join(missing)
