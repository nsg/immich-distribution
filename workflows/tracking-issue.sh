#!/bin/bash
set -eo pipefail

#
# This script monitores the upstream Immich repository for new releases and creates tracking issues 
#

. workflows/tools.sh

OLD_VERSION="$(cat VERSION)"
NEW_VERSION=$(get_latest_release)

#
# Validate version number, fail if not valid
#

if ! [[ "$NEW_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Version $NEW_VERSION is not a valid version number."
    exit 1
fi

#
# Only continue if there is a new version
#

if [ "$OLD_VERSION" == "$NEW_VERSION" ]; then
    echo "No new version available."
    exit 0
fi

#
# If there already is a tracking issue for this version, stop execute
#

if has_version_tracking_issue "$NEW_VERSION"; then
    echo "Tracking issue for $NEW_VERSION already exists."
    exit 0
fi

create_issue_body "$NEW_VERSION" | create_issue "$NEW_VERSION"
