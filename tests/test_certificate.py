from pathlib import Path

import httpx
import pytest

from helpers.command import run
from helpers.immich import ImmichApi
from helpers.snap import set_value, unset_value
from helpers.wait import eventually


CERT_DIR = Path("/var/snap/immich-distribution/common/acme/haproxy")
CERT_KEY = CERT_DIR / "cert.crt.key"
CERT_FILE = CERT_DIR / "cert.crt"


def wait_for_server(immich_url: str, client: httpx.Client) -> None:
    api = ImmichApi(immich_url, client)
    eventually(api.ping, timeout=180, interval=2)


def tcp_port_listening(port: int) -> bool:
    output = run(["sudo", "ss", "-tln"]).stdout
    return any(f":{port} " in line for line in output.splitlines())


def haproxy_frontends(client: httpx.Client, url: str) -> set[str]:
    response = client.get(url)
    response.raise_for_status()

    frontends: set[str] = set()
    for line in response.text.splitlines():
        fields = line.split(",")
        if len(fields) >= 2 and fields[1] == "FRONTEND":
            frontends.add(fields[0])
    return frontends


def generate_self_signed_certificate() -> None:
    run(["sudo", "mkdir", "-p", str(CERT_DIR)])
    run(["sudo", "openssl", "genrsa", "-out", str(CERT_KEY), "2048"])
    run(
        [
            "sudo",
            "openssl",
            "req",
            "-new",
            "-x509",
            "-key",
            str(CERT_KEY),
            "-out",
            str(CERT_FILE),
            "-days",
            "365",
            "-subj",
            "/C=US/ST=TestState/L=TestCity/O=TestOrg/CN=localhost",
        ]
    )

    certificate = run(["sudo", "openssl", "x509", "-in", str(CERT_FILE), "-text", "-noout"]).stdout
    assert "CN = localhost" in certificate


def log(message: str) -> None:
    print(message, flush=True)


@pytest.fixture
def clean_certificate_config(immich_url: str, http_client: httpx.Client):
    unset_value("https-enabled")
    unset_value("http-enabled")
    wait_for_server(immich_url, http_client)
    yield
    unset_value("https-enabled")
    unset_value("http-enabled")
    wait_for_server(immich_url, http_client)


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_manual_certificate_management(
    clean_certificate_config,
    immich_url: str,
    http_client: httpx.Client,
) -> None:
    log("Verify default HTTP-only configuration")
    wait_for_server(immich_url, http_client)

    eventually(lambda: tcp_port_listening(80) and not tcp_port_listening(443), timeout=60, interval=1)

    frontends = eventually(
        lambda: haproxy_frontends(http_client, "http://localhost/haproxy;csv"),
        timeout=60,
        interval=1,
    )
    assert "http" in frontends
    assert "https" not in frontends
    log("Default configuration exposes HTTP only")

    log("Generate self-signed certificate")
    generate_self_signed_certificate()
    log(f"Generated certificate for {CERT_FILE}")

    log("Enable HTTPS")
    set_value("https-enabled", "true")
    eventually(lambda: tcp_port_listening(80) and tcp_port_listening(443), timeout=60, interval=1)

    frontends = eventually(
        lambda: haproxy_frontends(http_client, "http://localhost/haproxy;csv"),
        timeout=60,
        interval=1,
    )
    assert "http" in frontends
    assert "https" in frontends
    log("HTTP and HTTPS frontends are both enabled")

    log("Disable HTTP")
    set_value("http-enabled", "false")
    eventually(lambda: not tcp_port_listening(80) and tcp_port_listening(443), timeout=60, interval=1)

    with httpx.Client(timeout=10.0, trust_env=False, verify=False) as https_client:
        https_frontends = eventually(
            lambda: haproxy_frontends(https_client, "https://localhost/haproxy;csv"),
            timeout=60,
            interval=1,
        )

    assert "https" in https_frontends
    assert "http" not in https_frontends
    log("HTTPS-only configuration is active")
