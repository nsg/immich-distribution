#!/usr/bin/env python3

"""
This test suite is a preparation suite for the Immich Distribution test suite.
Register a new user, generate API keys, and some simple validations.
"""

import socket
import os
from playwright.sync_api import Page, expect


def get_ip_address():
    immich_ip = os.getenv('IMMICH_IP')
    if immich_ip:
        return immich_ip

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


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


def get_input_by_label(page: Page, label_text: str, text=None):
    """Find input element by its label text and optionally fill it."""
    element = page.locator(f"//label[contains(text(), '{label_text}')]/..//input")
    if text:
        element.fill(text)
    return element


def test_prep_001_register(page: Page):
    """Register a new user"""
    immich_goto(page, login=False)
    
    # Welcome page, click button
    if "Welcome" in page.title():
        page.locator("span:has-text('Getting Started')").click()
    
    # Register a new user
    get_input_by_label(page, "Admin Email", "foo@example.com")
    get_input_by_label(page, "Admin Password", "secret")
    get_input_by_label(page, "Confirm Admin Password", "secret")
    get_input_by_label(page, "Name", "Ture Test")
    page.locator("button:has-text('Sign up')").click()
    
    expect(page).to_have_title("Login - Immich")


def test_prep_002_first_login(page: Page):
    """Login, follow the welcome flow and make sure we end up on the photos page."""
    immich_goto(page)
    
    expect(page).to_have_title("Onboarding - Immich")
    page.locator("button:has-text('Theme')").click()
    page.locator("button:has-text('Language')").click()
    page.locator("button:has-text('Server Privacy')").click()
    page.locator("button:has-text('User Privacy')").click()
    page.locator("button:has-text('Storage Template')").click()
    page.locator("button:has-text('Backups')").click()
    page.locator("button:has-text('Done')").click()
    expect(page).to_have_title("Photos - Immich")


def test_prep_003_empty_timeline(page: Page):
    """Make sure the timeline is empty and we get a message to upload photos."""
    immich_goto(page)
    expect(page.locator("p:has-text('CLICK TO UPLOAD YOUR FIRST PHOTO')")).to_be_visible()


def test_prep_004_generate_api_keys(page: Page):
    """
    Generate API keys and save them to a file called secret.txt.
    The API keys will be used by other tests to query the API and upload assets.
    """
    immich_goto(page, login=True)
    immich_goto(page, path="user-settings", login=False)
    page.locator("h2").wait_for()
    page.locator("button:has-text('API Keys')").click()
    page.locator("button:has-text('New API Key')").click()
    page.locator("button[id='input-select-all']").click()
    page.locator("button:has-text('Create')").click()
    secret = page.locator("textarea[id='secret']").text_content()
    with open("secret.txt", "w") as f:
        f.write(secret)
