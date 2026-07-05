import os

import httpx
import pytest

from helpers.command import run
from helpers.immich import ImmichApi


TEST_USER_EMAIL = os.environ.get("IMMICH_TEST_EMAIL", "foo@example.com")
TEST_KEY_NAME = "test-admin-api-key"
TEST_CHECK_KEY_NAME = "test-admin-api-key-check"


def create_admin_api_key(name: str, *, check: bool = False) -> str:
    command = [
        "sudo",
        "immich-distribution.immich-admin",
        "create-api-key",
        "--name",
        name,
    ]
    if check:
        command.append("--check")

    return run(command).stdout.strip()


def log(message: str) -> None:
    print(message, flush=True)


@pytest.mark.snap
def test_immich_admin_creates_usable_admin_api_key(immich_url: str, http_client: httpx.Client) -> None:
    api = ImmichApi(immich_url, http_client)

    log("Create admin API key with immich-admin")
    secret = create_admin_api_key(TEST_KEY_NAME)
    assert secret and len(secret) > 20

    log("Verify generated key authenticates")
    user = api.current_user(api_key=secret)
    assert user.get("email") == TEST_USER_EMAIL
    assert user.get("isAdmin") is True


@pytest.mark.snap
def test_immich_admin_check_mode_is_idempotent(immich_url: str, http_client: httpx.Client) -> None:
    api = ImmichApi(immich_url, http_client)

    log("Create admin API key with --check")
    secret = create_admin_api_key(TEST_CHECK_KEY_NAME, check=True)
    assert secret and len(secret) > 20

    log("Verify --check key authenticates")
    user = api.current_user(api_key=secret)
    assert user.get("email") == TEST_USER_EMAIL
    assert user.get("isAdmin") is True

    log("Run --check again and verify no duplicate key is created")
    repeated_secret = create_admin_api_key(TEST_CHECK_KEY_NAME, check=True)
    assert repeated_secret == ""
