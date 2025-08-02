#!/usr/bin/env python3

"""
This test suite is a preparation suite for the Immich Distribution test suite.
Register a new user, generate API keys, and some simple validations.
"""

import socket

from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

class TestImmichPrep(BaseCase):

    def immich(self, path=None, login=True):
        self.open(f"http://{get_ip_address()}")
        if login:
            self.login()
            self.sleep(2)
            if self.is_element_present("button:contains('Acknowledge')"):
                self.click("button:contains('Acknowledge')")

        if path:
            self.open(f"http://{get_ip_address()}/{path}")

    def login(self):
        self.type("input[id='email']", "foo@example.com")
        self.type("input[id='password']", "secret")
        self.click("button:contains('Login')")

    def write_message(self, message):
        self.open("about:blank")
        self.execute_script("document.body.style = 'font-family: sans-serif; padding: 40px 20px; font-size: 2em;'")
        self.execute_script(f'document.body.innerHTML="{message}";')

    def get_input_by_label(self, label_text, text=None):
        element = self.find_element(f"//label[contains(text(), '{label_text}')]/..//input")
        if text:
            element.send_keys(text)
        return element

    def test_prep_001_register(self):
        """
        Register a new user
        """

        self.immich(login=False)

        # Welcome page, click button
        if "Welcome" in self.get_title():
            self.click("span:contains('Getting Started')")

        # Register a new user
        self.get_input_by_label("Admin Email", "foo@example.com")
        self.get_input_by_label("Admin Password", "secret")
        self.get_input_by_label("Confirm Admin Password", "secret")
        self.get_input_by_label("Name", "Ture Test")
        self.click("button:contains('Sign up')")

        self.assert_title("Login - Immich")

    def test_prep_002_first_login(self):
        """
        Login, follow the welcome flow and make sure we end up on the photos page.
        """

        self.immich()

        self.assert_title("Onboarding - Immich")
        self.click("button:contains('Theme')")
        self.click("button:contains('Language')")
        self.click("button:contains('Server Privacy')")
        self.click("button:contains('User Privacy')")
        self.click("button:contains('Storage Template')")
        self.click("button:contains('Backups')")
        self.click("button:contains('Done')")
        self.assert_title("Photos - Immich")

    def test_prep_003_empty_timeline(self):
        """
        Make sure the timeline is empty and we get a message to upload photos.
        """

        self.immich()
        self.assert_element("p:contains('CLICK TO UPLOAD YOUR FIRST PHOTO')")

    def test_prep_004_generate_api_keys(self):
        """
        Generate API keys and save them to a file called secret.txt.
        The API keys will be used by other tests to query the API and upload assets.
        """
        self.immich(login=True)
        self.immich(login=False, path="user-settings")
        self.wait_for_element("h2")
        self.click("button:contains('API Keys')")
        self.click("button:contains('New API Key')")
        self.click("button[id='input-select-all']")
        self.click("button:contains('Create')")
        secret = self.get_text("textarea[id='secret']")
        with open("secret.txt", "w") as f:
            f.write(secret)
