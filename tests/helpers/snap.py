from __future__ import annotations

from helpers.command import run


SNAP_NAME = "immich-distribution"


def set_value(key: str, value: str) -> None:
    run(["sudo", "snap", "set", SNAP_NAME, f"{key}={value}"])


def unset_value(key: str) -> None:
    run(["sudo", "snap", "unset", SNAP_NAME, key])


def restart() -> None:
    run(["sudo", "snap", "restart", SNAP_NAME])
