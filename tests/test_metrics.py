import httpx
import pytest

from helpers.immich import ImmichApi
from helpers.metrics import assert_prometheus_format, fetch_metrics, http_status, metric_names
from helpers.snap import restart, set_value, unset_value
from helpers.wait import eventually


API_METRICS_URL = "http://127.0.0.1:8081/metrics"
MICROSERVICES_METRICS_URL = "http://127.0.0.1:8082/metrics"


def wait_for_server(immich_url: str, client: httpx.Client) -> None:
    api = ImmichApi(immich_url, client)
    eventually(api.ping, timeout=180, interval=2)


def reset_metrics_config(immich_url: str, client: httpx.Client) -> None:
    unset_value("metrics-telemetry-include")
    unset_value("metrics-telemetry-exclude")
    restart()
    wait_for_server(immich_url, client)


@pytest.fixture
def clean_metrics_config(immich_url: str, http_client: httpx.Client):
    reset_metrics_config(immich_url, http_client)
    yield
    reset_metrics_config(immich_url, http_client)


def apply_metrics_config(
    *,
    include: str | None,
    exclude: str | None,
    immich_url: str,
    client: httpx.Client,
) -> None:
    if include is None:
        unset_value("metrics-telemetry-include")
    else:
        set_value("metrics-telemetry-include", include)

    if exclude is None:
        unset_value("metrics-telemetry-exclude")
    else:
        set_value("metrics-telemetry-exclude", exclude)

    restart()
    wait_for_server(immich_url, client)


def wait_for_metrics(client: httpx.Client, url: str) -> str:
    return eventually(
        lambda: fetch_metrics(client, url) if http_status(client, url) == 200 else None,
        timeout=60,
        interval=1,
    )


def wait_for_metrics_disabled(client: httpx.Client, url: str) -> None:
    eventually(lambda: http_status(client, url) != 200, timeout=60, interval=1)


def has_metric_matching(names: set[str], pattern: str) -> bool:
    return any(pattern in name for name in names)


def log(message: str) -> None:
    print(message, flush=True)


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_metrics_include_and_exclude_control_exports(
    clean_metrics_config,
    immich_url: str,
    http_client: httpx.Client,
) -> None:
    log("Verify metrics are disabled by default")
    wait_for_metrics_disabled(http_client, API_METRICS_URL)
    wait_for_metrics_disabled(http_client, MICROSERVICES_METRICS_URL)
    log("Default metrics endpoints are disabled")

    log("Enable all metrics")
    apply_metrics_config(include="all", exclude=None, immich_url=immich_url, client=http_client)
    all_api_body = wait_for_metrics(http_client, API_METRICS_URL)
    all_microservices_body = wait_for_metrics(http_client, MICROSERVICES_METRICS_URL)

    assert_prometheus_format(all_api_body, "API")
    assert_prometheus_format(all_microservices_body, "Microservices")

    all_api_names = metric_names(all_api_body)
    assert has_metric_matching(all_api_names, "process_cpu")
    log(f"include=all exported {len(all_api_names)} API metric families")

    log("Enable API-only metrics")
    apply_metrics_config(include="api", exclude=None, immich_url=immich_url, client=http_client)
    api_only_body = wait_for_metrics(http_client, API_METRICS_URL)
    assert_prometheus_format(api_only_body, "API-only")

    api_only_names = metric_names(api_only_body)
    assert api_only_names != all_api_names
    assert api_only_names < all_api_names
    assert not has_metric_matching(api_only_names, "process_cpu")
    log(f"include=api exported {len(api_only_names)} API metric families")

    log("Exclude API metrics")
    apply_metrics_config(include="all", exclude="api", immich_url=immich_url, client=http_client)
    all_except_api_body = wait_for_metrics(http_client, API_METRICS_URL)
    assert_prometheus_format(all_except_api_body, "Exclude API")

    all_except_api_names = metric_names(all_except_api_body)
    assert all_except_api_names != all_api_names
    assert all_except_api_names < all_api_names
    assert api_only_names - all_except_api_names
    assert has_metric_matching(all_except_api_names, "process_cpu")
    log(f"exclude=api exported {len(all_except_api_names)} API metric families")

    log("Disable metrics again")
    reset_metrics_config(immich_url, http_client)
    wait_for_metrics_disabled(http_client, API_METRICS_URL)
    wait_for_metrics_disabled(http_client, MICROSERVICES_METRICS_URL)
    log("Metrics endpoints are disabled after reset")
