#!/usr/bin/env python3

import socket
import os
import requests
import time
import glob
from datetime import datetime
import uuid
from playwright.sync_api import Page, expect


def get_ip_address():
    immich_ip = os.getenv('IMMICH_IP')
    if immich_ip:
        return immich_ip

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def get_secret():
    with open("secret.txt", "r") as f:
        return f.read()

def get_headers():
    return {
        "Accept": "application/json",
        "X-API-KEY": get_secret()
    }

def get_assets(filter=[]):
    ret = {}

    for f in filter:
        r = requests.post(
            f"http://{get_ip_address()}/api/search/metadata",
            headers=get_headers(),
            json={"originalFileName": f}
        )

        asset = r.json()['assets']['items']
        if len(asset) != 1:
            raise Exception(f"Expected 1 asset, got {len(asset)}")

        r = requests.get(f"http://{get_ip_address()}/api/assets/{asset[0]['id']}", headers=get_headers())
        ret[f] = r.json()

    return ret

def get_number_of_assets() -> int:
    r = requests.get(f"http://{get_ip_address()}/api/server/statistics", headers=get_headers())
    response = r.json()
    return response['photos'] + response['videos']

def get_all_jobs():
    r = requests.get(f"http://{get_ip_address()}/api/jobs", headers=get_headers())
    return r.json()

def trigger_job(job_name):
    r = requests.put(
        f"http://{get_ip_address()}/api/jobs/{job_name}",
        headers=get_headers(),
        json={"command": "start"}
    )
    return r.json()

def wait_for_empty_job_queue():
    while True:
        time.sleep(1)
        running_or_paused_jobs = 0
        for _, job_data in get_all_jobs().items():
            paused = True
            active = True

            if isinstance(job_data, dict) and 'queueStatus' in job_data and isinstance(job_data['queueStatus'], dict):
                paused = job_data['queueStatus']['isPaused']
                active = job_data['queueStatus']['isActive']

            if paused or active:
                running_or_paused_jobs += 1

        if running_or_paused_jobs == 0:
            break

def css_selector_path(element):
    """ Returns a CSS selector that will uniquely select the given element. """
    path = []
    while element.parent:
        siblings = element.parent.find_all(element.name, recursive=False)
        if len(siblings) > 1:
            index = siblings.index(element)
            path.insert(0, f"{element.name}:nth-child({index+1})")
        else:
            path.insert(0, element.name)
        element = element.parent

    return " > ".join(path)

def import_asset(path):
    stats = os.stat(path)

    data = {
        "deviceAssetId": f"{path}-{uuid.uuid4()}",
        "deviceId": "pytest",
        "fileCreatedAt": datetime.fromtimestamp(stats.st_mtime),
        "fileModifiedAt": datetime.fromtimestamp(stats.st_mtime),
        "isFavorite": "false",
    }

    files = {"assetData": open(path, 'rb')}

    response = requests.post(
        f"http://{get_ip_address()}/api/assets", headers=get_headers(), data=data, files=files
    )

    if response.status_code != 201:
        raise Exception(f"Failed to upload asset {path}, status code {response.status_code}. Response: {response.text}")

    return response.json()


def immich_goto(page: Page, path=None, login=True):
    """Navigate to Immich and optionally login."""
    page.goto(f"http://{get_ip_address()}")
    
    if login:
        immich_login(page)
        page.wait_for_timeout(2000)
        
        acknowledge_button = page.locator("button:has-text('Acknowledge')")
        if acknowledge_button.is_visible():
            acknowledge_button.click()
    
    if path:
        page.goto(f"http://{get_ip_address()}/{path}")


def immich_login(page: Page):
    """Login to Immich."""
    page.locator("input[id='email']").fill("foo@example.com")
    page.locator("input[id='password']").fill("secret")
    page.locator("button:has-text('Login')").click()


def write_message(page: Page, message: str):
    """Display a message on a blank page."""
    page.goto("about:blank")
    page.evaluate("document.body.style = 'font-family: sans-serif; padding: 40px 20px; font-size: 2em;'")
    page.evaluate(f'document.body.innerHTML="{message}";')


def test_selenium_001_empty_timeline(page: Page):
    """Make sure the timeline is empty and we get a message to upload photos."""
    immich_goto(page)
    expect(page.locator("p:has-text('CLICK TO UPLOAD YOUR FIRST PHOTO')")).to_be_visible()


def test_selenium_005_upload_assets_via_api(page: Page):
    """
    Upload test assets to the server using the API. I maintain a list of testfiles in assets/
    The Makefile that runs this script should have cloned a specific version of the test-assets
    repo from the upstream Immich repo that I handpicked a few interesting files from.
    """
    test_images = [
        "assets/ai-apple.tiff",
        "assets/ai-people1.png",
        "assets/ai-people2.png",
        "assets/ai-people3.png",
        "assets/ml-tesla1.png",
        "assets/ml-tesla2.png",
        "assets/ml-tesla3.png",
        "assets/ml-tesla4.png",
        "assets/ml-tesla5.png",
        "assets/ml-tesla6.png",
        "assets/ml-edison1.png",
        "assets/ml-edison2.png",
        "assets/ml-edison3.png",
        "assets/ml-edison4.png",
        "assets/field.jpg",
        "assets/grass.MP.jpg",
        "assets/memory.jpg",
        "assets/ohm.gif",
        "assets/plane.jpg",
        "assets/ship.mp4",
        "assets/ship-vp9.webm",
        "assets/PXL_20250712_111801796.jpg",
        "test-assets/formats/heic/IMG_2682.heic",
        "test-assets/formats/webp/denali.webp",
        "test-assets/formats/raw/Nikon/D80/glarus.nef",
        "test-assets/formats/raw/Nikon/D700/philadelphia.nef",
    ]

    for test_image in test_images:
        write_message(page, f"API: Uploading {test_image}")
        r = import_asset(test_image)
        assert r.get('id') is not None


def test_selenium_006_wait_for_job_queue(page: Page):
    """
    Wait for the job queue to be empty, this tests verifies that the image
    processing jobs are running and that the queue is empty when they are done.
    """
    write_message(page, "API: Wait for the job queue to be empty")
    wait_for_empty_job_queue()

    write_message(page, "API: Trigger the face detection job")
    trigger_job("faceDetection")
    time.sleep(2)

    write_message(page, "API: Wait for the job queue to be empty (again)")
    wait_for_empty_job_queue()


def test_selenium_100_verify_uploaded_assets_number_of_files(page: Page):
    """Use the API to verify that the assets were uploaded correctly."""
    write_message(page, "API: Query the API and verify that the number of assets is correct")
    assert get_number_of_assets() == 26


def test_selenium_100_verify_exif_location_extraction(page: Page):
    """
    Extract the location from the EXIF data and verify that it is parses
    correctly as a named location.
    """
    write_message(page, "API: Verify that the location is extracted correctly from the EXIF data")
    assets = get_assets(["ship.mp4", "grass.MP.jpg"])

    ship = assets['ship.mp4']
    grass = assets['grass.MP.jpg']

    assert ship['type'] == "VIDEO"
    assert ship['exifInfo']['country'] == "Sweden"
    assert grass['exifInfo']['city'] == "Mora"


def test_selenium_100_verify_image_exitdata(page: Page):
    """Extract the EXIF data from the images and verify that it is correct."""
    write_message(page, "API: Verify that the EXIF data is extracted correctly")
    assets = get_assets(["ohm.gif", "grass.MP.jpg", "IMG_2682.heic"])
    ohm = assets['ohm.gif']
    grass = assets['grass.MP.jpg']
    heic = assets['IMG_2682.heic']

    assert ohm['type'] == "IMAGE"
    assert ohm['exifInfo']['exifImageWidth'] == 640

    assert grass['type'] == "IMAGE"
    assert grass['exifInfo']['model'] == "Pixel 4"
    assert grass['exifInfo']['dateTimeOriginal'] == "2023-07-08T12:13:53.21+00:00"
    assert grass['exifInfo']['city'] == "Mora"

    assert heic['type'] == "IMAGE"
    assert heic['exifInfo']['model'] == "iPhone 7"
    assert heic['exifInfo']['dateTimeOriginal'] == "2019-03-21T16:04:22.348+00:00"
    assert heic['exifInfo']['country'] == "United States of America"


def test_selenium_100_verify_people_detected(page: Page):
    """
    Query the API to verify that people were detected in the images.
    This test will try 10 times if there are no people detected in the images.
      * The face recognition model works
      * Pgvector extension works
    """
    write_message(page, "API: Verify that people are detected in the images")
    wait_for_empty_job_queue()

    with open("secret.txt", "r") as f:
        secret = f.read()

    headers = { "X-API-KEY": secret }

    for _ in range(10):
        r = requests.get(f"http://{get_ip_address()}/api/people", headers=headers)
        people = r.json()

        if people['total'] == 0:
            time.sleep(2)
            continue

        assert people['total'] > 1
        break


def get_asset_ocr(asset_id: str) -> list:
    """Get OCR data for an asset."""
    r = requests.get(
        f"http://{get_ip_address()}/api/assets/{asset_id}/ocr",
        headers=get_headers()
    )
    return r.json()


def test_selenium_100_verify_ocr_extraction(page: Page):
    """
    Verify that OCR (Optical Character Recognition) works correctly.
    This tests that:
      * The OCR processing job runs
      * Text is extracted from images containing text
    """
    write_message(page, "API: Verify that OCR extracts text from images")
    wait_for_empty_job_queue()

    # Get the test image that contains text
    assets = get_assets(["PXL_20250712_111801796.jpg"])
    ocr_test_asset = assets["PXL_20250712_111801796.jpg"]

    # Get OCR data for the asset
    ocr_data = get_asset_ocr(ocr_test_asset['id'])

    # Verify OCR data was extracted
    assert len(ocr_data) > 0, "Expected OCR data to be extracted from image with text"

    # Verify the OCR response structure
    first_ocr = ocr_data[0]
    assert 'text' in first_ocr, "OCR response should contain 'text' field"
    assert 'textScore' in first_ocr, "OCR response should contain 'textScore' field"
    assert len(first_ocr['text']) > 0, "OCR text should not be empty"

    # Combine all OCR text and verify expected content is found
    all_text = " ".join([item['text'].upper() for item in ocr_data])
    assert "WORLD" in all_text or "UNDERGROUND" in all_text, \
        f"Expected to find 'WORLD' or 'UNDERGROUND' in OCR text, got: {all_text}"
