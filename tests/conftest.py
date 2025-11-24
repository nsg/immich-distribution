"""
Pytest configuration for Playwright tests.
Handles browser setup and video recording.
"""

import os
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
def video_path(request):
    """Directory for video recordings."""
    video_dir = Path("test-results") / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    return video_dir
