import pytest

from helpers.immich import ImmichApi
from helpers.wait import eventually


@pytest.mark.snap
def test_server_ping_responds(immich_url, http_client) -> None:
    api = ImmichApi(immich_url, http_client)

    eventually(api.ping, timeout=120, interval=2)
