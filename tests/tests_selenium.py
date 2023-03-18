#!/usr/bin/env python3

import socket
import time
from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


class TestImmichWeb(BaseCase):

    def immich(self):
        self.open(f"http://{get_ip_address()}")

    def register_or_login(self):
        self.immich()

        # Welcome page, click button
        if "Welcome" in self.get_title():
            self.click("button")

        if "Login" in self.get_title():
            self.type("input[id='email']", "foo@example.com")
            self.type("input[id='password']", "secret")
            self.click("button")
        else:
            self.type("input[id='email']", "foo@example.com")
            self.type("input[id='password']", "secret")
            self.type("input[id='confirmPassword']", "secret")
            self.type("input[id='firstName']", "Ture")
            self.type("input[id='lastName']", "Test")
            self.click("button")

    def test_click_getting_started_and_register(self):
        self.register_or_login()

    def test_immich_log_in(self):
        self.register_or_login()
        self.assert_title("Photos - Immich")

    def x_test_immich_upload_image(self):
        self.register_or_login()
        #self.click("//section[1]/section/div/section/button[2]")
        self.open_new_window()
        self.open("file:///assets/minne.jpg")
        time.sleep(5)
