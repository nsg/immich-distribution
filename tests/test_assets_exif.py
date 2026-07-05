import httpx
import pytest

from helpers.assets import EXIF_TEST_ASSETS, get_asset_by_id, log, upload_assets, wait_for_empty_job_queue


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_extracts_exif_and_location_metadata(immich_url: str, http_client: httpx.Client) -> None:
    uploaded = upload_assets(http_client, immich_url, EXIF_TEST_ASSETS)

    log("Wait for asset processing queue to drain")
    wait_for_empty_job_queue(http_client, immich_url)

    log("Verify EXIF and location extraction")
    ship = get_asset_by_id(http_client, immich_url, uploaded["ship.mp4"]["id"])
    grass = get_asset_by_id(http_client, immich_url, uploaded["grass.MP.jpg"]["id"])
    assert ship["type"] == "VIDEO"
    assert ship["exifInfo"]["country"] == "Sweden"
    assert grass["exifInfo"]["city"] == "Mora"

    log("Verify image EXIF data")
    ohm = get_asset_by_id(http_client, immich_url, uploaded["ohm.gif"]["id"])
    heic = get_asset_by_id(http_client, immich_url, uploaded["IMG_2682.heic"]["id"])
    assert ohm["type"] == "IMAGE"
    assert ohm["exifInfo"]["exifImageWidth"] == 640
    assert grass["type"] == "IMAGE"
    assert grass["exifInfo"]["model"] == "Pixel 4"
    assert grass["exifInfo"]["dateTimeOriginal"] == "2023-07-08T12:13:53.21+00:00"
    assert heic["type"] == "IMAGE"
    assert heic["exifInfo"]["model"] == "iPhone 7"
    assert heic["exifInfo"]["dateTimeOriginal"] == "2019-03-21T16:04:22.348+00:00"
    assert heic["exifInfo"]["country"] == "United States of America"
