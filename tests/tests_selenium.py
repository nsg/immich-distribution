#!/usr/bin/env python3

import socket
import time
import subprocess
from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


class TestImmichWeb(BaseCase):

    def immich(self, path=""):
        self.open(f"http://{get_ip_address()}/{path}")

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

    def test_001_click_getting_started_and_register(self):
        self.immich()
        self.register()

    def test_002_immich_log_in(self):
        self.immich()
        self.login()
        self.assert_title("Photos - Immich")

    def test_010_immich_create_token_and_upload_file(self):
        self.immich()
        self.login()
        time.sleep(2)
        self.immich("user-settings")
        self.click("/html/body/div/section[2]/section[2]/section/section/div[3]/div/button")
        self.click("//button[.='New API Key']")
        self.type("//input[@id='name']", "Selenium")
        self.click("//button[.='Create']")
        key = self.get_text("//textarea[@id='secret']")
        self.click("//button[.='Done']")
        upload = subprocess.run([
            "immich-distribution.cli", "upload",
            "--key", key,
            "-d", "/var/snap/immich-distribution/current/",
            "--yes"
        ])
        assert upload.returncode == 0
        time.sleep(10)
        self.immich("photos")
        self.click("/html/body/div[1]/section[2]/section[2]/section/div[2]/div/section/div/div/div/div/img[1]")
        time.sleep(2)
