import re
import time

import httpx
import pytest
from playwright.sync_api import Page, expect

from helpers.assets import (
    ALL_TEST_ASSETS,
    headers,
    log,
    trigger_job,
    upload_assets,
    wait_for_empty_job_queue,
    wait_for_thumbnails,
)
from helpers.wait import eventually
from helpers.web import (
    BrowserErrorWatcher,
    log_in,
    recorded_browser_page,
)


ASSET_VIEWER_URL = re.compile(r".*/photos/(?P<id>[0-9a-fA-F-]{36})")
TIMELINE_ONLY_URL = re.compile(r".*/photos([?#].*)?$")
EXPLORE_URL = re.compile(r".*/explore([?#].*)?$")
VIEWER_SELECTOR = "#immich-asset-viewer"

# Explore only lists a place once at least five images share a city, and
# the uploaded test assets have at most two, so give a batch of images
# the same location through the API.
PLACE_ASSETS = [
    "ml-tesla1.png",
    "ml-tesla2.png",
    "ml-tesla3.png",
    "ml-tesla4.png",
    "ml-tesla5.png",
    "ml-tesla6.png",
]
STOCKHOLM_LATITUDE = 59.3293
STOCKHOLM_LONGITUDE = 18.0686


def set_asset_locations(client: httpx.Client, immich_url: str, uploaded: dict) -> list[str]:
    ids = [uploaded[name]["id"] for name in PLACE_ASSETS]
    response = client.put(
        f"{immich_url}/api/assets",
        headers=headers(),
        json={"ids": ids, "latitude": STOCKHOLM_LATITUDE, "longitude": STOCKHOLM_LONGITUDE},
    )
    assert response.status_code == 204, response.text
    return ids


def refresh_asset_metadata(client: httpx.Client, immich_url: str, ids: list[str]) -> None:
    # The location update writes the coordinates to an XMP sidecar; a
    # metadata refresh then reads the sidecar and reverse geocodes the
    # coordinates into a city.
    response = client.post(
        f"{immich_url}/api/assets/jobs",
        headers=headers(),
        json={"assetIds": ids, "name": "refresh-metadata"},
    )
    assert response.status_code in (200, 201, 204), response.text


def wait_for_explore_places(client: httpx.Client, immich_url: str) -> None:
    def places_populated() -> bool:
        response = client.get(f"{immich_url}/api/search/explore", headers=headers())
        assert response.status_code == 200, response.text

        for field in response.json():
            if field.get("fieldName") == "exifInfo.city" and field.get("items"):
                return True
        return False

    eventually(places_populated, timeout=120, interval=2)


def wait_for_people_detected(client: httpx.Client, immich_url: str) -> None:
    def people_total() -> int | None:
        response = client.get(f"{immich_url}/api/people", headers=headers())
        assert response.status_code == 200, response.text

        total = response.json()["total"]
        return total if total > 0 else None

    eventually(people_total, timeout=60, interval=2)


def current_asset_id(page: Page) -> str:
    match = ASSET_VIEWER_URL.match(page.url)
    assert match, f"not in the asset viewer: {page.url}"
    return match.group("id")


def wait_for_viewer_media(page: Page) -> None:
    # The viewer shows an img for photos and a video element for videos,
    # both with the asset id in the source URL. Scope to the viewer
    # overlay: the timeline underneath keeps a hidden grid thumbnail
    # whose src contains the same asset id.
    asset_id = current_asset_id(page)
    media = page.locator(
        f'{VIEWER_SELECTOR} img[src*="{asset_id}"], {VIEWER_SELECTOR} video[src*="{asset_id}"]'
    ).first
    expect(media).to_be_visible(timeout=30000)


def open_sidebar_page(page: Page, name: str, url_pattern: re.Pattern) -> None:
    log(f"Open {name} from the sidebar")
    page.get_by_role("link", name=name).first.click()
    page.wait_for_url(url_pattern, timeout=15000)
    page.wait_for_load_state("networkidle", timeout=15000)


def return_to_explore(page: Page) -> None:
    # Person and search pages replace the sidebar with a top bar whose
    # back button is labelled Close and returns to the previous page.
    log("Return to Explore")
    page.get_by_role("button", name="Close").first.click()
    page.wait_for_url(EXPLORE_URL, timeout=15000)
    page.wait_for_load_state("networkidle", timeout=15000)


@pytest.mark.snap
@pytest.mark.timeout(900)
def test_populated_timeline_and_asset_viewer(immich_url: str, http_client: httpx.Client) -> None:
    log("Upload test assets")
    uploaded = upload_assets(http_client, immich_url, ALL_TEST_ASSETS)

    log("Wait for asset processing queue to drain")
    wait_for_empty_job_queue(http_client, immich_url)

    log("Verify every asset has a thumbnail")
    wait_for_thumbnails(http_client, immich_url, uploaded)

    log("Set a shared location on a batch of images")
    place_asset_ids = set_asset_locations(http_client, immich_url, uploaded)
    wait_for_empty_job_queue(http_client, immich_url)

    log("Refresh metadata to reverse geocode the location")
    refresh_asset_metadata(http_client, immich_url, place_asset_ids)
    wait_for_empty_job_queue(http_client, immich_url)
    wait_for_explore_places(http_client, immich_url)

    # Recognition of new faces is deferred by the server, so trigger it
    # explicitly or the People section on Explore stays empty.
    log("Trigger face detection")
    trigger_job(http_client, immich_url, "faceDetection")
    time.sleep(2)
    wait_for_empty_job_queue(http_client, immich_url)
    wait_for_people_detected(http_client, immich_url)

    with recorded_browser_page() as page:
        watcher = BrowserErrorWatcher(page)

        log("Log in through browser")
        log_in(page)

        log("Verify timeline shows uploaded assets")
        # Login already lands on the timeline; a hard navigation here
        # aborts in-flight requests and the app logs those as errors.
        thumbnails = page.locator("[data-asset-id]")
        expect(thumbnails.first).to_be_visible(timeout=30000)
        assert thumbnails.count() >= 5, "timeline rendered fewer thumbnails than expected"

        log("Open a photo in the asset viewer")
        thumbnails.first.click()
        page.wait_for_url(ASSET_VIEWER_URL, timeout=15000)
        wait_for_viewer_media(page)

        # The video player grabs keyboard focus once a video plays, so
        # drive the viewer with its buttons instead of arrow keys.
        viewer = page.locator(VIEWER_SELECTOR)

        log("Step through a few assets")
        for _ in range(3):
            previous_asset_id = current_asset_id(page)
            viewer.get_by_role("button", name="View next asset").click()
            expect(page).not_to_have_url(re.compile(f".*{previous_asset_id}.*"), timeout=15000)
            wait_for_viewer_media(page)

        log("Close the asset viewer")
        viewer.get_by_role("button", name="Go back").click()
        page.wait_for_url(TIMELINE_ONLY_URL, timeout=15000)

        open_sidebar_page(page, "Explore", EXPLORE_URL)

        log("Open a person from Explore")
        person_link = page.locator('a[href^="/people/"]').first
        expect(person_link).to_be_visible(timeout=15000)
        person_link.click()
        page.wait_for_url(re.compile(r".*/people/[0-9a-fA-F-]{36}.*"), timeout=15000)
        page.wait_for_load_state("networkidle", timeout=15000)

        return_to_explore(page)

        log("Open a place from Explore")
        # Place cards link to /search?query=...; a bare /search href is
        # the app header's search button.
        place_link = page.locator('a[href*="/search?"]').first
        expect(place_link).to_be_visible(timeout=15000)
        place_link.click()
        page.wait_for_url(re.compile(r".*/search.*"), timeout=15000)
        page.wait_for_load_state("networkidle", timeout=15000)

        return_to_explore(page)

        # The map page appends a position hash to the URL as soon as the
        # map initializes, so allow a trailing query or fragment.
        open_sidebar_page(page, "Map", re.compile(r".*/map([?#].*)?$"))
        log("Wait for the map to render")
        expect(page.locator("canvas").first).to_be_visible(timeout=30000)

        open_sidebar_page(page, "Albums", re.compile(r".*/albums([?#].*)?$"))

        open_sidebar_page(page, "Photos", TIMELINE_ONLY_URL)
        log("Verify timeline thumbnails again")
        expect(thumbnails.first).to_be_visible(timeout=15000)

        log("Verify no serious browser errors were observed")
        watcher.assert_no_serious_errors()
