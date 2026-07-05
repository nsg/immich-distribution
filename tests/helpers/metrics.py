from __future__ import annotations

import httpx


def http_status(client: httpx.Client, url: str) -> int | None:
    try:
        return client.get(url).status_code
    except httpx.HTTPError:
        return None


def fetch_metrics(client: httpx.Client, url: str) -> str:
    response = client.get(url)
    response.raise_for_status()
    return response.text


def metric_names(body: str) -> set[str]:
    names: set[str] = set()

    for line in body.splitlines():
        if not line or line.startswith("#"):
            continue

        name = line.split(maxsplit=1)[0].split("{", maxsplit=1)[0]
        for suffix in ("_bucket", "_sum", "_count"):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break
        names.add(name)

    if not names:
        raise AssertionError("failed to extract metric names from Prometheus output")

    return names


def assert_prometheus_format(body: str, label: str) -> None:
    lines = body.splitlines()
    assert any(line.startswith("# HELP") for line in lines), f"{label} metrics missing HELP lines"
    assert any(line.startswith("# TYPE") for line in lines), f"{label} metrics missing TYPE lines"
