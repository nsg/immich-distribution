"""
Pytest configuration for Playwright tests.
Handles browser setup, video recording, and timeouts.
"""

import pytest
import re
import shutil
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
def set_timeouts_and_save_video(page, context, request, video_path):
    """Set timeouts and save video with test name after test."""
    page.set_default_timeout(ACTION_TIMEOUT)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT)
    yield
    test_name = re.sub(r'[^a-zA-Z0-9_-]', '-', request.node.name)
    video_file = video_path / f"{test_name}.webm"
    video_src = page.video.path()
    context.close()
    shutil.move(str(video_src), str(video_file))


def pytest_configure(config):
    """Configure expect timeout globally."""
    from playwright.sync_api import expect
    expect.set_options(timeout=EXPECT_TIMEOUT)
