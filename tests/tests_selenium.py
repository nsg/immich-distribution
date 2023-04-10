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

    def test_001_register_and_login(self):
        self.immich()
        self.register()
        self.login()
        time.sleep(20)
        self.assert_title("Photos - Immich")
