import csv
from io import StringIO

import httpx
import pytest

from helpers.immich import ImmichApi
from helpers.wait import eventually


HAPROXY_STATS_URL = "http://localhost/haproxy;csv"


def haproxy_rows(client: httpx.Client) -> list[dict[str, str]]:
    response = client.get(HAPROXY_STATS_URL)
    response.raise_for_status()

    lines = response.text.splitlines()
    assert lines, "HAProxy stats response was empty"

    header = lines[0].lstrip("# ").split(",")
    reader = csv.DictReader(StringIO("\n".join(lines[1:])), fieldnames=header)
    return list(reader)


def find_row(rows: list[dict[str, str]], pxname: str, svname: str) -> dict[str, str] | None:
    for row in rows:
        if row.get("pxname") == pxname and row.get("svname") == svname:
            return row
    return None


def log(message: str) -> None:
    print(message, flush=True)


@pytest.mark.snap
@pytest.mark.timeout(600)
def test_haproxy_default_proxy_and_backend_health(immich_url: str, http_client: httpx.Client) -> None:
    api = ImmichApi(immich_url, http_client)

    log("Verify Immich is reachable through the default HAProxy route")
    eventually(api.ping, timeout=180, interval=2)

    log("Fetch HAProxy stats CSV")
    rows = eventually(lambda: haproxy_rows(http_client), timeout=60, interval=1)

    log("Verify default HTTP frontend and expected backend checks")
    assert find_row(rows, "http", "FRONTEND") is not None
    assert find_row(rows, "stats", "BACKEND") is not None

    checked_backends = [
        ("be_server", "immich-server"),
        ("be_ml", "ml"),
        ("be_postgres", "postgres"),
        ("be_redis", "redis"),
    ]

    def all_backends_up() -> bool:
        # Backends report transitional states like "DOWN 1/2" or "UP 1/3"
        # while health checks settle, so require a plain "UP" for each.
        current_rows = haproxy_rows(http_client)
        not_up = []
        for pxname, svname in checked_backends:
            row = find_row(current_rows, pxname, svname)
            if row is None:
                not_up.append(f"{pxname}/{svname}: missing from stats")
            elif row.get("status") != "UP":
                not_up.append(f"{pxname}/{svname}: {row.get('status')}")

        assert not not_up, "HAProxy backends are not UP: " + ", ".join(not_up)
        return True

    log("Wait for all backends to report UP")
    eventually(all_backends_up, timeout=240, interval=5)
