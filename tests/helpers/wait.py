from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


def eventually(check: Callable[[], T], *, timeout: float = 60.0, interval: float = 1.0) -> T:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except Exception as error:
            last_error = error

        time.sleep(interval)

    if last_error is not None:
        raise AssertionError(f"condition was not met within {timeout:.0f}s") from last_error

    raise AssertionError(f"condition was not met within {timeout:.0f}s")
