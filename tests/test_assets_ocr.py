import httpx
import pytest

from helpers.assets import OCR_TEST_ASSETS, headers, log, upload_assets, wait_for_empty_job_queue


def assert_ocr_extracted(client: httpx.Client, immich_url: str, asset_id: str) -> None:
    response = client.get(f"{immich_url}/api/assets/{asset_id}/ocr", headers=headers())
    assert response.status_code == 200, response.text

    ocr_data = response.json()
    assert ocr_data, "expected OCR data to be extracted from image with text"
    assert "text" in ocr_data[0], "OCR response should contain 'text' field"
    assert "textScore" in ocr_data[0], "OCR response should contain 'textScore' field"
    assert ocr_data[0]["text"], "OCR text should not be empty"

    all_text = " ".join(item["text"].upper() for item in ocr_data)
    assert "WORLD" in all_text or "UNDERGROUND" in all_text, (
        f"expected to find 'WORLD' or 'UNDERGROUND' in OCR text, got: {all_text}"
    )


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_extracts_ocr_text(immich_url: str, http_client: httpx.Client) -> None:
    uploaded = upload_assets(http_client, immich_url, OCR_TEST_ASSETS)

    log("Wait for asset processing queue to drain")
    wait_for_empty_job_queue(http_client, immich_url)

    log("Verify OCR extraction")
    assert_ocr_extracted(http_client, immich_url, uploaded["PXL_20250712_111801796.jpg"]["id"])
