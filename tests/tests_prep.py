#!/usr/bin/env python3

"""
This test suite is a preparation suite for the Immich Distribution test suite.
Register a new user, generate API keys, and some simple validations.
"""

import socket
import os
from playwright.sync_api import Page, expect


def debug(message: str):
    """Print debug message with immediate flush for real-time output."""
    print(f"[DEBUG] {message}", flush=True)


def get_ip_address():
    immich_ip = os.getenv('IMMICH_IP')
    if immich_ip:
        return immich_ip

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def immich_goto(page: Page, path=None, login=True):
    """Navigate to Immich and optionally login."""
    url = f"http://{get_ip_address()}"
    debug(f"Navigating to {url}")
    page.goto(url)
    
    if login:
        immich_login(page)
        
        acknowledge_button = page.locator("button:has-text('Acknowledge')")
        if acknowledge_button.is_visible():
            debug("Clicking 'Acknowledge' button")
            acknowledge_button.click()
    
    if path:
        full_url = f"http://{get_ip_address()}/{path}"
        debug(f"Navigating to {full_url}")
        page.goto(full_url)


def immich_login(page: Page):
    """Login to Immich."""
    debug("Filling email field")
    page.locator("input[id='email']").fill("foo@example.com")

    debug("Filling password field")
    page.locator("input[id='password']").fill("secret")

    debug("Clicking 'Login' button")
    page.locator("button:has-text('Login')").click()
    
    debug("Waiting for navigation after login")
    page.wait_for_url(lambda url: "/auth/login" not in url, timeout=60000)


def write_message(page: Page, message: str):
    """Display a message on a blank page."""
    page.goto("about:blank")
    page.evaluate("document.body.style = 'font-family: sans-serif; padding: 40px 20px; font-size: 2em;'")
    page.evaluate(f'document.body.innerHTML="{message}";')


def test_prep_001_register(page: Page):
    """Register a new user"""
    immich_goto(page, login=False)
    
    debug("Clicking 'Getting Started' button")
    page.locator("span:has-text('Getting Started')").click()
    
    debug("Filling email field")
    page.locator("input[type='email']").fill("foo@example.com")

    debug("Filling password field")
    page.locator("input[type='password']").nth(0).fill("secret")

    debug("Filling confirm password field")
    page.locator("input[type='password']").nth(1).fill("secret")

    debug("Filling name field")
    page.locator("input[type='text']").fill("Ture Test")
    
    debug("Clicking 'Sign up' button")
    page.locator("button:has-text('Sign up')").click()
    
    debug("Verifying redirect to login page")
    expect(page).to_have_title("Login - Immich")


def test_prep_002_first_login(page: Page):
    """Login, follow the welcome flow and make sure we end up on the photos page."""
    immich_goto(page)
    
    debug("Verifying onboarding page title")
    expect(page).to_have_title("Onboarding - Immich")
    
    debug("Clicking 'Theme' button")
    page.get_by_role("button", name="Theme").click()

    debug("Clicking 'Language' button")
    page.get_by_role("button", name="Language").click()

    debug("Clicking 'Server Privacy' button")
    page.get_by_role("button", name="Server Privacy").click()

    debug("Clicking 'User Privacy' button")
    page.get_by_role("button", name="User Privacy").click()

    debug("Clicking 'Storage Template' button")
    page.get_by_role("button", name="Storage Template").click()

    debug("Clicking 'Backups' button")
    page.get_by_role("button", name="Backups").click()

    debug("Clicking 'Mobile App' button")
    page.get_by_role("button", name="Mobile App").click()

    debug("Clicking 'Done' button")
    page.get_by_role("button", name="Done").click()
    
    debug("Verifying photos page title")
    expect(page).to_have_title("Photos - Immich")


def test_prep_003_empty_timeline(page: Page):
    """Make sure the timeline is empty and we get a message to upload photos."""
    immich_goto(page)
    
    debug("Verifying empty timeline message is visible")
    expect(page.locator("p:has-text('CLICK TO UPLOAD YOUR FIRST PHOTO')")).to_be_visible()


def test_prep_004_generate_api_keys(page: Page):
    """
    Generate API keys and save them to a file called secret.txt.
    The API keys will be used by other tests to query the API and upload assets.
    """
    immich_goto(page, login=True)
    
    debug("Navigating to user-settings")
    immich_goto(page, path="user-settings", login=False)

    debug("Waiting for API Keys section to be visible")
    page.get_by_role("button", name="API Keys").wait_for()
    
    debug("Clicking 'API Keys' button")
    page.get_by_role("button", name="API Keys").click()
    
    debug("Clicking 'New API Key' button")
    page.get_by_role("button", name="New API Key").click()

    debug("Clicking 'Select All' button")
    page.locator("button[id='input-select-all']").click()

    debug("Clicking 'Create' button")
    page.get_by_role("button", name="Create").click()
    
    debug("Waiting for secret textarea to appear")
    page.locator("textarea").wait_for()
    
    debug("Reading API key from textarea")
    secret = page.locator("textarea").input_value()

    debug("Validating API key")
    assert secret and len(secret) > 20, f"API key should be a non-empty string, got: '{secret}'"

    debug("Saving API key to secret.txt")
    with open("secret.txt", "w") as f:
        f.write(secret)
    debug(f"API key saved ({len(secret)} chars)")
