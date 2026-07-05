import time

import httpx
import pytest

from helpers.assets import PEOPLE_TEST_ASSETS, headers, log, trigger_job, upload_assets, wait_for_empty_job_queue
from helpers.wait import eventually


def assert_people_detected(client: httpx.Client, immich_url: str) -> None:
    def detected_count() -> int | None:
        response = client.get(f"{immich_url}/api/people", headers=headers())
        assert response.status_code == 200, response.text

        total = response.json()["total"]
        return total if total > 1 else None

    total = eventually(detected_count, timeout=60, interval=2)
    assert total > 1


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_detects_people(immich_url: str, http_client: httpx.Client) -> None:
    upload_assets(http_client, immich_url, PEOPLE_TEST_ASSETS)

    log("Wait for asset processing queue to drain")
    wait_for_empty_job_queue(http_client, immich_url)

    log("Trigger face detection")
    trigger_job(http_client, immich_url, "faceDetection")
    time.sleep(2)
    wait_for_empty_job_queue(http_client, immich_url)

    log("Verify people detection")
    assert_people_detected(http_client, immich_url)
