import httpx
import pytest

from helpers.assets import (
    ALL_TEST_ASSETS,
    get_number_of_assets,
    log,
    upload_assets,
    wait_for_empty_job_queue,
    wait_for_thumbnails,
)


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_upload_supported_asset_formats(immich_url: str, http_client: httpx.Client) -> None:
    before = get_number_of_assets(http_client, immich_url)
    uploaded = upload_assets(http_client, immich_url, ALL_TEST_ASSETS)

    log("Wait for asset processing queue to drain")
    wait_for_empty_job_queue(http_client, immich_url)

    log("Verify uploaded asset count")
    after = get_number_of_assets(http_client, immich_url)
    assert after - before == len(ALL_TEST_ASSETS)
    assert len(uploaded) == len(ALL_TEST_ASSETS)

    log("Verify every asset has a thumbnail")
    wait_for_thumbnails(http_client, immich_url, uploaded)
