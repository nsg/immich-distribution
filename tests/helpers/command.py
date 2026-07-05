from __future__ import annotations

import subprocess
from collections.abc import Sequence


def run(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode == 0:
        return result

    command = " ".join(args)
    raise AssertionError(
        f"command failed with exit code {result.returncode}: {command}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
