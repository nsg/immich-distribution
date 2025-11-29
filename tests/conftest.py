"""
Pytest configuration for Playwright tests.
Handles browser setup, video recording, and timeouts.
"""

import pytest
import re
from pathlib import Path


# Timeout settings (in milliseconds for Playwright)
ACTION_TIMEOUT = 300_000      # 300s for clicks, fills, etc.
NAVIGATION_TIMEOUT = 300_000  # 300s for page.goto()
EXPECT_TIMEOUT = 300_000      # 300s for expect() assertions

# Video directory
VIDEO_DIR = Path("test-results") / "videos"


@pytest.fixture(scope="session")
def video_path():
    """Directory for video recordings."""
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    return VIDEO_DIR


@pytest.fixture
def browser_context_args(browser_context_args, video_path: Path):
    """Configure browser context with video recording (per-test context)."""
    browser_context_args["record_video_dir"] = str(video_path)
    browser_context_args["record_video_size"] = {"width": 1280, "height": 720}
    browser_context_args["viewport"] = {"width": 1280, "height": 720}
    return browser_context_args


@pytest.fixture(autouse=True)
def set_timeouts_and_save_video(page, request, video_path):
    """Set timeouts and save video with test name after test."""
    page.set_default_timeout(ACTION_TIMEOUT)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
    yield
    # Close page first (required by Playwright before save_as)
    page.close()
    # Sanitize test name: keep only alphanumeric, dash, underscore
    test_name = re.sub(r'[^a-zA-Z0-9_-]', '-', request.node.name)
    video_file = video_path / f"{test_name}.webm"
    page.video.save_as(video_file)
    page.video.delete()


def pytest_configure(config):
    """Configure expect timeout globally."""
    from playwright.sync_api import expect
    expect.set_options(timeout=EXPECT_TIMEOUT)
