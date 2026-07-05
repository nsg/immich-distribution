import os

import httpx
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-snap-tests",
        action="store_true",
        default=False,
        help="Run tests that require a running Immich Distribution server.",
    )
    parser.addoption(
        "--run-migration-tests",
        action="store_true",
        default=False,
        help="Run tests that verify documented migration paths.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    skip_snap = pytest.mark.skip(reason="requires --run-snap-tests")
    skip_migration = pytest.mark.skip(reason="requires --run-migration-tests")

    for item in items:
        if "snap" in item.keywords and not config.getoption("--run-snap-tests"):
            item.add_marker(skip_snap)
        if "migration" in item.keywords and not config.getoption("--run-migration-tests"):
            item.add_marker(skip_migration)


@pytest.fixture(scope="session")
def immich_url() -> str:
    return os.environ.get("IMMICH_URL", "http://localhost").rstrip("/")


@pytest.fixture
def http_client() -> httpx.Client:
    with httpx.Client(timeout=10.0, trust_env=False) as client:
        yield client
