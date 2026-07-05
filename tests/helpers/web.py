import os
import re
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
    sync_playwright,
)


IMMICH_URL = os.environ.get("IMMICH_URL", "http://localhost").rstrip("/")
TEST_USER_EMAIL = os.environ.get("IMMICH_TEST_EMAIL", "foo@example.com")
TEST_USER_PASSWORD = os.environ.get("IMMICH_TEST_PASSWORD", "secret")
VIDEO_DIR = Path(os.environ.get("PLAYWRIGHT_VIDEO_DIR", "runtime/videos"))
# Pace browser actions so the recorded videos are easy to follow.
SLOW_MO_MS = int(os.environ.get("PLAYWRIGHT_SLOW_MO_MS", "2000"))
SERIOUS_RESOURCE_TYPES = {"document", "script", "stylesheet", "image", "font"}
API_RESOURCE_TYPES = {"xhr", "fetch"}
TIMELINE_URL = re.compile(r".*/photos([/?#].*)?$")


def log(message: str) -> None:
    print(message, flush=True)


def request_failure_text(request) -> str:
    failure = request.failure
    if callable(failure):
        failure = failure()
    return str(failure or "")


def failed_request_message(request) -> str | None:
    error_text = request_failure_text(request)
    if "net::ERR_ABORTED" in error_text:
        return None
    return f"{request.resource_type}: {request.url}: {error_text}"


def record_failed_request(request, failed_requests: list[str]) -> None:
    message = failed_request_message(request)
    if message is not None:
        failed_requests.append(message)


def bad_response_message(response) -> str | None:
    resource_type = response.request.resource_type
    status = response.status

    if resource_type in API_RESOURCE_TYPES:
        # Auth probes and optional lookups legitimately return 4xx, so
        # only server errors count for API calls.
        if status < 500:
            return None
    elif resource_type not in SERIOUS_RESOURCE_TYPES or status < 400:
        return None

    return f"{status}: {resource_type}: {response.url}"


def record_bad_response(response, bad_responses: list[str]) -> None:
    message = bad_response_message(response)
    if message is not None:
        bad_responses.append(message)


class BrowserErrorWatcher:
    def __init__(self, page: Page):
        self.failed_requests: list[str] = []
        self.bad_responses: list[str] = []
        self.console_errors: list[str] = []
        self.page_errors: list[str] = []

        page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        page.on(
            "console",
            lambda message: self.console_errors.append(message.text)
            if message.type in {"error", "assert"}
            else None,
        )
        page.on(
            "requestfailed",
            lambda request: record_failed_request(request, self.failed_requests),
        )
        page.on(
            "response",
            lambda response: record_bad_response(response, self.bad_responses),
        )

    def assert_no_serious_errors(self) -> None:
        serious_failed_requests = [
            failure for failure in self.failed_requests if not failure.startswith("websocket:")
        ]
        assert not serious_failed_requests, "browser requests failed:\n" + "\n".join(serious_failed_requests)
        assert not self.bad_responses, "browser assets returned HTTP errors:\n" + "\n".join(self.bad_responses)
        assert not self.page_errors, "browser page errors:\n" + "\n".join(self.page_errors)
        # "Failed to fetch" is the console echo of requests aborted by
        # navigation (net::ERR_ABORTED), which record_failed_request
        # already tolerates.
        serious_console_errors = [
            error for error in self.console_errors if "Failed to fetch" not in error
        ]
        assert not serious_console_errors, "browser console errors:\n" + "\n".join(serious_console_errors)


@contextmanager
def recorded_browser_page():
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(slow_mo=SLOW_MO_MS)
        context = browser.new_context(
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720},
        )
        page = context.new_page()
        try:
            yield page
        finally:
            context.close()
            browser.close()


def visible_button(page: Page, name: str):
    button = page.get_by_role("button", name=name).first
    try:
        button.wait_for(state="visible", timeout=1500)
    except PlaywrightTimeoutError:
        return None
    return button


def dismiss_update_dialog(page: Page) -> None:
    button = visible_button(page, "Acknowledge")
    if button is not None:
        button.click()


def log_in(page: Page) -> None:
    page.goto(IMMICH_URL, wait_until="networkidle")

    email = page.locator("input[id='email'], input[type='email']").first
    expect(email).to_be_visible(timeout=10000)
    email.fill(TEST_USER_EMAIL)
    page.locator("input[id='password'], input[type='password']").first.fill(TEST_USER_PASSWORD)
    page.get_by_role("button", name="Login").click()

    # Landing on the timeline proves authentication worked and that test
    # prep already completed onboarding; anything else (still on the login
    # page, onboarding wizard) fails here.
    page.wait_for_url(TIMELINE_URL, timeout=30000)
    page.wait_for_load_state("networkidle", timeout=30000)

    dismiss_update_dialog(page)
