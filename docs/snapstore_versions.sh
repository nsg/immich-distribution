#!/usr/bin/env bash
set -euo pipefail

API_URL="https://api.snapcraft.io/v2/snaps/info/immich-distribution"
OUTPUT_FILE="site/snapstore-data.json"

echo "Fetching snap store data..."

response=$(curl -sS -H "Snap-Device-Series: 16" "$API_URL")

if [ -z "$response" ]; then
    echo "Error: Empty response from snap store API" >&2
    exit 1
fi

channel_map=$(echo "$response" | jq -r '.["channel-map"]')

if [ "$channel_map" = "null" ] || [ -z "$channel_map" ]; then
    echo "Error: No channel-map data found" >&2
    exit 1
fi

echo "$response" | jq '{
    channels: [
        .["channel-map"][] | {
            channel: .channel.name,
            revision: .revision,
            version: .version,
            released: (.channel["released-at"] | 
                split("T")[0] |
                split("-") |
                (.[1] | tonumber) as $month |
                (.[2] | tonumber) as $day |
                ([
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ][$month - 1]) + " " + ($day | tostring) + ", " + .[0])
        }
    ],
    latest_stable_revision: (
        [.["channel-map"][] | 
         select(.channel.name == "latest/stable" or .channel.name == "stable") | 
         .revision] | 
        if length > 0 then max else 0 end
    ),
    latest_stable_version: (
        [.["channel-map"][] | 
         select(.channel.name == "latest/stable" or .channel.name == "stable")] |
        if length > 0 then
            (max_by(.revision) | .version)
        else
            ""
        end
    )
}' > "$OUTPUT_FILE"

latest_version=$(jq -r '.latest_stable_version' "$OUTPUT_FILE")
latest_revision=$(jq -r '.latest_stable_revision' "$OUTPUT_FILE")

echo "Wrote snap store data to $OUTPUT_FILE"
echo "Latest stable: $latest_version (rev $latest_revision)"
