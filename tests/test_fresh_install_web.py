import re

import pytest
from playwright.sync_api import Page, expect

from helpers.web import (
    IMMICH_URL,
    BrowserErrorWatcher,
    dismiss_update_dialog,
    log,
    log_in,
    recorded_browser_page,
)


def click_around(page: Page) -> int:
    candidate_names = [
        "Photos",
        "Explore",
        "Albums",
        "Sharing",
        "Favorites",
        "Archive",
        "Utilities",
        "Administration",
    ]

    # The sidebar must be rendered before the visibility checks below,
    # which do not wait.
    expect(page.get_by_role("link", name="Photos").first).to_be_visible(timeout=15000)

    clicks = 0
    for name in candidate_names:
        link = page.get_by_role("link", name=name)
        button = page.get_by_role("button", name=name)
        target = link.first if link.count() else button.first

        if not target.is_visible():
            log(f"Skip {name}: not visible")
            continue

        log(f"Open {name}")
        target.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        dismiss_update_dialog(page)
        clicks += 1

        if clicks >= 3:
            break

    return clicks


@pytest.mark.snap
def test_browser_login_assets_console_and_navigation() -> None:
    with recorded_browser_page() as page:
        watcher = BrowserErrorWatcher(page)

        log("Log in through browser")
        log_in(page)

        log("Verify Immich web app shell loaded")
        expect(page).to_have_title(re.compile("Immich"), timeout=30000)

        log("Navigate through a few app surfaces")
        clicks = click_around(page)
        assert clicks >= 3, f"expected to navigate at least 3 app surfaces, clicked {clicks}"

        log("Verify no serious browser errors were observed")
        watcher.assert_no_serious_errors()

        # Cosmetic only, so the video ends on the timeline. A hard
        # navigation aborts in-flight requests and the app logs those
        # as errors, so this must stay after the error assertion.
        log("Return to the timeline")
        page.goto(f"{IMMICH_URL}/photos", wait_until="networkidle")
