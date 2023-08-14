#!/usr/bin/env python3

import socket
import os
import subprocess
import shutil
import requests

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

class TestImmichWeb(BaseCase):

    def immich(self, path="", login=True):
        self.open(f"http://{get_ip_address()}/{path}")
        if login:
            self.login()
            self.sleep(2)
            if self.is_element_present("button:contains('Acknowledge')"):
                self.click("button:contains('Acknowledge')")

    def register(self):
        # Welcome page, click button
        if "Welcome" in self.get_title():
            self.click("button")

        self.type("input[id='email']", "foo@example.com")
        self.type("input[id='password']", "secret")
        self.type("input[id='confirmPassword']", "secret")
        self.type("input[id='firstName']", "Ture")
        self.type("input[id='lastName']", "Test")
        self.click("button")

    def login(self):
        self.type("input[id='email']", "foo@example.com")
        self.type("input[id='password']", "secret")
        self.click("button")
        self.wait_for_element("p:contains('Photos')")

    def test_001_register_and_login(self):
        """
        Register a new user and login, make sure we end up on the photos page.
        """
        if not is_dirty_state():
            self.immich(login=False)
            self.register()
            self.login()
            self.assert_title("Photos - Immich")

    def test_002_no_errors(self):
        """
        Make sure there are no JS or 404 errors on the page before and after login.
        """
        self.immich(login=False)
        self.assert_no_js_errors()
        self.assert_no_404_errors()
        self.login()
        self.assert_no_js_errors()
        self.assert_no_404_errors()

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
        soup = self.get_beautiful_soup()
        api_keys_div = soup.find(string="API Keys").parent.parent.parent
        api_keys_button = api_keys_div.find("button")
        self.click(css_selector_path(api_keys_button))
        self.click("button:contains('New API Key')")
        self.type("input[id='name']", "test\n")
        secret = self.get_text("textarea[id='secret']")
        with open("secret.txt", "w") as f:
            f.write(secret)

    def test_10_verify_cli(self):
        """
        Verify that the CLI is installed and can be executed.
        """
        p = subprocess.run(["immich-distribution.cli", "-h"])
        self.assertEqual(p.returncode, 0)

    def test_005_upload_assets_with_cli(self):
        """
        Use the CLI to upload assets from the assets/ directory.
        """
        secret = get_secret()
        
        snap_readable_path = os.path.join(
            os.environ["HOME"],
            "snap/immich-distribution/current/tests"
        )

        if not os.path.exists(snap_readable_path):
            os.makedirs(snap_readable_path)

        for upload in os.listdir("assets"):
            shutil.copy(f"assets/{upload}", snap_readable_path)

        subprocess.run(
            [
                "immich-distribution.cli",
                "upload",
                "--key", secret,
                "--yes",
                snap_readable_path
            ]
        )

        # Give the system time to process the new assets
        self.sleep(60)

    def test_100_verify_uploaded_assets(self):
        """
        Query the API to get a list of assets, this mainly tests that:
          * The assets are there (upload works)
          * The exif extraction works
          * The live photo detection works
          * FFmpeg transcoding works
        """

        secret = get_secret()
        headers = { "X-API-KEY": secret }

        r = requests.get(f"http://{get_ip_address()}/api/asset", headers=headers)
        assets = r.json()
        self.assertEqual(len(assets), 11)

        for asset in assets:
            match asset['originalFileName']:
                case "ship":
                    self.assertEqual(asset['type'], "VIDEO")
                    self.assertEqual(asset['exifInfo']['country'], "Sweden")
                case "ship-vp9":
                    self.assertEqual(asset['type'], "VIDEO")

                    r = requests.get(f"http://{get_ip_address()}/api/asset/file/{asset['id']}?isThumb=false&isWeb=true", headers=headers)
                    self.assertEqual(r.status_code, 200)
                    self.assertEqual(r.headers['content-type'], "video/mp4")
                case "ohm":
                    self.assertEqual(asset['type'], "IMAGE")
                    self.assertEqual(asset['exifInfo']['exifImageWidth'], 640)
                case "grass.MP":
                    self.assertEqual(asset['type'], "IMAGE")
                    self.assertEqual(asset['exifInfo']['model'], "Pixel 4")
                    self.assertEqual(asset['exifInfo']['dateTimeOriginal'], "2023-07-08T12:13:53.000Z")
                    self.assertEqual(asset['exifInfo']['city'], "Mora")
                    self.assertNotEqual(asset['livePhotoVideoId'], None)
                case "plane":
                    pass
                case "field":
                    pass
                case "memory":
                    pass
                case "ai-people1":
                    pass
                case "ai-people2":
                    pass
                case "ai-people3":
                    pass
                case "ai-apple":
                    pass
                case _:
                    raise Exception(asset)

    def test_100_verify_people_detected(self):
        """
        Query the API to get a list of assets, this mainly tests that:
          * The ML model works and detects people
          * Typesese works (used to generate embeddings)
        """
        with open("secret.txt", "r") as f:
            secret = f.read()

        headers = { "X-API-KEY": secret }

        # query the API to get a list of people
        r = requests.get(f"http://{get_ip_address()}/api/person", headers=headers)
        people = r.json()
        self.assertEqual(people['total'], 6)
