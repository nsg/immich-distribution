import os
from pathlib import Path

import httpx
import pytest

from helpers.immich import ImmichApi
from helpers.wait import eventually


TEST_USER_EMAIL = os.environ.get("IMMICH_TEST_EMAIL", "foo@example.com")
TEST_USER_PASSWORD = os.environ.get("IMMICH_TEST_PASSWORD", "secret")
TEST_USER_NAME = os.environ.get("IMMICH_TEST_NAME", "Ture Test")
API_KEY_FILE = Path(os.environ.get("API_KEY_FILE", "runtime/artifacts/api-key.txt"))


def log(message: str) -> None:
    print(message, flush=True)


def write_api_key(secret: str) -> None:
    API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    API_KEY_FILE.write_text(secret)
    log(f"Wrote API key to {API_KEY_FILE}")


@pytest.mark.snap
def test_prepare_immich_api_user_and_key(immich_url: str, http_client: httpx.Client) -> None:
    api = ImmichApi(immich_url, http_client)

    log("Wait for Immich server")
    eventually(api.ping, timeout=180, interval=2)

    log(f"Create or reuse admin user {TEST_USER_EMAIL}")
    api.create_admin_user(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, name=TEST_USER_NAME)

    log("Login as test user")
    access_token = api.login(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)

    log("Complete onboarding")
    api.complete_admin_onboarding(access_token=access_token)
    api.complete_user_onboarding(access_token=access_token)

    log("Disable new version check")
    api.disable_version_check(access_token=access_token)

    log("Create API key")
    secret = api.create_api_key(access_token=access_token, name="ci-test", permissions=["all"])

    log("Verify API key authentication")
    user = api.current_user(api_key=secret)
    assert user.get("email") == TEST_USER_EMAIL

    write_api_key(secret)
