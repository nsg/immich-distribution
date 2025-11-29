"""
Pytest configuration for Playwright tests.
Handles browser setup and video recording.
"""

import pytest
from pathlib import Path


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, video_path: Path):
    """Configure browser context with video recording."""
    browser_context_args["record_video_dir"] = str(video_path)
    browser_context_args["record_video_size"] = {"width": 1280, "height": 720}
    browser_context_args["viewport"] = {"width": 1280, "height": 720}
    return browser_context_args


@pytest.fixture(scope="session")
def video_path():
    """Directory for video recordings."""
    video_dir = Path("test-results") / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    return video_dir


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach video to failed tests in pytest-html report."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        video_dir = Path("test-results") / "videos"
        if video_dir.exists():
            videos = sorted(video_dir.glob("*.webm"), key=lambda p: p.stat().st_mtime, reverse=True)
            if videos:
                latest_video = videos[0]
                video_path = f"../test-results/videos/{latest_video.name}"
                extra = getattr(report, "extras", [])
                extra.append(pytest_html_extras_video(video_path, latest_video.name))
                report.extras = extra


def pytest_html_extras_video(path, name):
    """Create an extra item for video in pytest-html."""
    return {
        "name": name,
        "format_type": "video",
        "content": path,
    }
