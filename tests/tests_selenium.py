#!/usr/bin/env python3

import socket
import os
import requests
import time
import glob
from datetime import datetime
import uuid

from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def is_dirty_state():
    return os.getenv("DIRTY_STATE")

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

def get_number_of_assets():
    r = requests.get(f"http://{get_ip_address()}/api/server-info/statistics", headers=get_headers())
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

            # Validate the API response, we got a integer inside queueStatus instead of a dict
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


class TestImmichWeb(BaseCase):

    def immich(self, path="", login=True):
        self.open(f"http://{get_ip_address()}/{path}")
        if login:
            self.login()
            self.sleep(2)
            if self.is_element_present("button:contains('Acknowledge')"):
                self.click("button:contains('Acknowledge')")

    def login(self):
        self.type("input[id='email']", "foo@example.com")
        self.type("input[id='password']", "secret")
        self.click("button:contains('Login')")

    def test_001_register(self):
        """
        Register a new user
        """

        self.immich(login=False)

        # Welcome page, click button
        if "Welcome" in self.get_title():
            self.click("button")

        # Register a new user
        self.type("input[id='email']", "foo@example.com")
        self.type("input[id='password']", "secret")
        self.type("input[id='confirmPassword']", "secret")
        self.type("input[id='name']", "Ture Test")
        self.click("button:contains('Sign up')")

        self.assert_title("Login - Immich")

    def test_002_first_login(self):
        """
        Login, follow the welcome flow and make sure we end up on the photos page.
        """

        self.immich()

        # Check that we are on the onboarding page
        self.assert_title("Onboarding - Immich")

        # Press on "Theme" to select a theme
        self.click("button:contains('Theme')")

        # Press on "Storage Template" to manage storage templates
        self.click("button:contains('Storage template')")

        # Do not enable the storage template feature, just click "Done"
        self.click("button:contains('Done')")

        # Verify that we are on the photos page
        self.assert_title("Photos - Immich")

    def test_003_empty_timeline(self):
        """
        Make sure the timeline is empty and we get a message to upload photos.
        """
        if not is_dirty_state():
            self.immich()
            self.assert_element("p:contains('CLICK TO UPLOAD YOUR FIRST PHOTO')")

    def test_004_generate_api_keys(self):
        """
        Generate API keys and save them to a file called secret.txt.
        The API keys will be used by other tests to query the API and upload assets.
        """
        self.immich(login=True)
        self.immich(login=False, path="user-settings")
        self.wait_for_element("h2")
        self.click("button:contains('API Keys')")
        self.click("button:contains('New API Key')")
        self.type("input[id='name']", "test\n")
        secret = self.get_text("textarea[id='secret']")
        with open("secret.txt", "w") as f:
            f.write(secret)

    def test_005_configure_immich(self):
        """
        Configure Immich via the API
        """

        old_config = requests.get(f"http://{get_ip_address()}/api/system-config", headers=get_headers())
        self.assertEqual(old_config.status_code, 200)

        data=old_config.json()
        data["machineLearning"]["facialRecognition"]["minFaces"] = 1

        response = requests.put(
            f"http://{get_ip_address()}/api/system-config", headers=get_headers(), json=data
        )
        self.assertEqual(response.status_code, 200)

    def test_005_upload_assets_via_api(self):
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
            "assets/field.jpg",
            "assets/grass.MP.jpg",
            "assets/memory.jpg",
            "assets/ohm.gif",
            "assets/plane.jpg",
            "assets/ship.mp4",
            "assets/ship-vp9.webm",
            "test-assets/formats/heic/IMG_2682.heic",
            "test-assets/formats/webp/denali.webp",
            "test-assets/formats/raw/Nikon/D80/glarus.nef",
            "test-assets/formats/raw/Nikon/D700/philadelphia.nef",
        ]

        for test_image in test_images:
            r = import_asset(test_image)
            self.assertNotEqual(r.get('id'), None)

        # ML models are downloaded in the background when we upload assets
        # Wait for them to complete, and the queue to be empty before continuing
        wait_for_empty_job_queue()

        # # Re-run the recognition job. I'm not sure if this is an Immich bug or
        # # just a quirk of the test environment. Anyway let's just run it again.
        trigger_job("faceDetection")
        time.sleep(2)
        wait_for_empty_job_queue()

    def test_100_verify_uploaded_assets_number_of_files(self):
        """
        Use the API to verify that the assets were uploaded correctly.
        """
        self.assertEqual(get_number_of_assets(), 15)

    def test_100_verify_exif_location_extraction(self):
        """
        Extract the location from the EXIF data and verify that it is parses
        correctly as a named location.
        """

        assets = get_assets(["ship.mp4", "grass.MP.jpg"])

        ship = assets['ship.mp4']
        grass = assets['grass.MP.jpg']

        print(ship)

        self.assertEqual(ship['type'], "VIDEO")
        self.assertEqual(ship['exifInfo']['country'], "Sweden")
        self.assertEqual(grass['exifInfo']['city'], "Mora")

    def test_100_verify_image_exitdata(self):
        """
        Extract the EXIF data from the images and verify that it is correct.
        """

        assets = get_assets(["ohm.gif", "grass.MP.jpg", "IMG_2682.heic"])
        ohm = assets['ohm.gif']
        grass = assets['grass.MP.jpg']
        heic = assets['IMG_2682.heic']

        self.assertEqual(ohm['type'], "IMAGE")
        self.assertEqual(ohm['exifInfo']['exifImageWidth'], 640)

        self.assertEqual(grass['type'], "IMAGE")
        self.assertEqual(grass['exifInfo']['model'], "Pixel 4")
        self.assertEqual(grass['exifInfo']['dateTimeOriginal'], "2023-07-08T12:13:53.210Z")
        self.assertEqual(grass['exifInfo']['city'], "Mora")

        self.assertEqual(heic['type'], "IMAGE")
        self.assertEqual(heic['exifInfo']['model'], "iPhone 7")
        self.assertEqual(heic['exifInfo']['dateTimeOriginal'], "2019-03-21T16:04:22.348Z")
        self.assertEqual(heic['exifInfo']['country'], "United States of America")

    def test_100_verify_people_detected(self):
        """
        Query the API to verify that people were detected in the images.
        This test will try 10 times if there are no people detected in the images.
          * The face recognition model works
          * Pgvector extension works
        """

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

            self.assertGreater(people['total'], 2)
