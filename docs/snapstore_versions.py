import requests
import json
from datetime import datetime


def on_page_content(html, page, config, files):
    if page.title == "Installation":

        api_url = f"https://api.snapcraft.io/v2/snaps/info/immich-distribution"
        headers = {"Snap-Device-Series": "16"}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            repl_data = "<table class=\"snapstore-versions\"><tr><th>Channel</th><th>Revision</th><th>Version</th><th>Released</th></tr>"
            for x in response.json()['channel-map']:
                released_at = x['channel']['released-at']
                released_date = datetime.fromisoformat(released_at)
                formatted_date = released_date.strftime("%B %d, %Y")
                repl_data += f"<tr><td>{x['channel']['name']}</td><td>{x['revision']}</td><td>{x['version']}</td><td>{formatted_date}</td></tr>"
            repl_data += "</table>"
        else:
            repl_data = f"Error {response.status_code}: {response.text}"

        html = html.replace("{{snapstore_versions}}", repl_data)

    return html
