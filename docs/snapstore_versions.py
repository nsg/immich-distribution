import requests
import re
from datetime import datetime, timezone


def _fetch_snap_info():
    api_url = "https://api.snapcraft.io/v2/snaps/info/immich-distribution"
    headers = {"Snap-Device-Series": "16"}
    return requests.get(api_url, headers=headers, timeout=5)


def _build_versions_table(data):
    table = "<table class=\"snapstore-versions\"><tr><th>Channel</th><th>Revision</th><th>Version</th><th>Released</th></tr>"
    for x in data:
        released_at = x['channel']['released-at']
        ra = released_at.replace('Z', '+00:00')
        released_date = datetime.fromisoformat(ra)
        if released_date.tzinfo is None:
            released_date = released_date.replace(tzinfo=timezone.utc)
        formatted_date = released_date.astimezone(timezone.utc).strftime("%B %d, %Y")
        table += f"<tr><td>{x['channel']['name']}</td><td>{x['revision']}</td><td>{x['version']}</td><td>{formatted_date}</td></tr>"
    table += "</table>"
    return table


def _latest_stable_revision(data):
    latest = ""
    for x in data:
        if x['channel']['name'] in ("latest/stable", "stable"):
            if not latest or x['revision'] > latest:
                latest = x['revision']
    return latest


def _latest_stable_version(data):
    version = ""
    latest_rev = None
    for x in data:
        if x['channel']['name'] in ("latest/stable", "stable"):
            rev = x['revision']
            if latest_rev is None or rev > latest_rev:
                latest_rev = rev
                version = x['version']
    return version


def on_page_content(html, page, config, files):
    if not re.search(r"{{[^}]+}}", html):
        return html
    macros = {
        "{{snapstore_versions}}": lambda data: _build_versions_table(data),
        "{{snapstore_revision}}": lambda data: str(_latest_stable_revision(data)),
        "{{snapstore_version}}": lambda data: _latest_stable_version(data),
        "{{snapstore_revision_old}}": lambda data: (lambda rev: str(int(rev) - 5) if rev else "")(_latest_stable_revision(data)),
        "{{snapstore_revision_oldish}}": lambda data: (lambda rev: str(int(rev) - 4) if rev else "")(_latest_stable_revision(data)),
        "{{snapstore_revision_newish}}": lambda data: (lambda rev: str(int(rev) - 2) if rev else "")(_latest_stable_revision(data)),
        "{{snapstore_revision_block}}": lambda data: (lambda rev: str(int(rev) - 3) if rev else "")(_latest_stable_revision(data)),
    }
    needed = [m for m in macros if m in html]
    if not needed:
        return html
    try:
        response = _fetch_snap_info()
    except Exception as e:
        for m in needed:
            html = html.replace(m, f"Error fetching snap info: {e}")
        return html
    if response.status_code != 200:
        err = f"Error {response.status_code}: {response.text}"
        for m in needed:
            html = html.replace(m, err)
        return html
    data = response.json().get('channel-map', [])
    for m in needed:
        html = html.replace(m, macros[m](data))
    return html
