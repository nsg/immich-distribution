#!/bin/bash
set -eo pipefail

#
# This script monitores the tracking issues and updates them if necessary
#

. workflows/tools.sh

TRACKING_ISSUES="$(list_tracking_issues)"

if [ -z "$TRACKING_ISSUES" ]; then
    echo "No tracking issues found."
    exit 0
fi

for issue_number in $TRACKING_ISSUES; do
    get_issue_body $issue_number > /tmp/ISSUE-BODY.md
    cp /tmp/ISSUE-BODY.md /tmp/ISSUE-BODY.md.original
    VERSION_MAJOR_MINOR=$(get_issue_title $issue_number | awk '{ print $2 }')
    NEW_VERSION=$(get_latest_release_for_major_minor $VERSION_MAJOR_MINOR)
    NEW_VERSION_MAJOR_MINOR=$(echo $NEW_VERSION | cut -d. -f1-2)

    echo
    echo "Process issue $issue_number (tracking version $VERSION_MAJOR_MINOR, latest version $NEW_VERSION)"

    # Add release link if not already there
    if grep -qE "https.*releases\/tag\/$NEW_VERSION" /tmp/ISSUE-BODY.md; then
        echo "Release link for $NEW_VERSION already exists."
    else
        sed -i "/https.*releases\/tag\/v.*/a * https://github.com/immich-app/immich/releases/tag/$NEW_VERSION" /tmp/ISSUE-BODY.md
    fi

    #
    # Update the snapcraft channels with release information
    #

    CURRENT_DATE=$(date +%F)
    EDGE_VERSION="$(snapstore_version edge)"
    BETA_VERSION="$(snapstore_version beta)"
    CANDIDATE_VERSION="$(snapstore_version candidate)"
    STABLE_VERSION="$(snapstore_version stable)"

    if [[ $EDGE_VERSION == $NEW_VERSION_MAJOR_MINOR* ]] && ! grep -q "| Edge | $EDGE_VERSION" /tmp/ISSUE-BODY.md; then
        echo "Edge version $EDGE_VERSION is a release under the $NEW_VERSION_MAJOR_MINOR release, update the table."
        sed -i "s/^| Edge |[^|]*|[^|]*|/| Edge | $EDGE_VERSION | $CURRENT_DATE |/" /tmp/ISSUE-BODY.md
    fi

    if [[ $BETA_VERSION == $NEW_VERSION_MAJOR_MINOR* ]] && ! grep -q "| Beta | $EDGE_VERSION" /tmp/ISSUE-BODY.md; then
        echo "Beta version $BETA_VERSION is a release under the $NEW_VERSION_MAJOR_MINOR release, update the table."
        sed -i "s/^| Beta |[^|]*|[^|]*|/| Beta | $BETA_VERSION | $CURRENT_DATE |/" /tmp/ISSUE-BODY.md
    fi

    if [[ $CANDIDATE_VERSION == $NEW_VERSION_MAJOR_MINOR* ]] && ! grep -q "| Candidate | $EDGE_VERSION" /tmp/ISSUE-BODY.md; then
        echo "Candidate version $CANDIDATE_VERSION is a release under the $NEW_VERSION_MAJOR_MINOR release, update the table."
        sed -i "s/^| Candidate |[^|]*|[^|]*|/| Candidate | $CANDIDATE_VERSION | $CURRENT_DATE |/" /tmp/ISSUE-BODY.md
    fi

    if [[ $STABLE_VERSION == $NEW_VERSION_MAJOR_MINOR* ]] && ! grep -q "| Stable | $EDGE_VERSION" /tmp/ISSUE-BODY.md; then
        echo "Stable version $STABLE_VERSION is a release under the $NEW_VERSION_MAJOR_MINOR release, update the table."
        sed -i "s/^| Stable |[^|]*|[^|]*|/| Stable | $STABLE_VERSION | $CURRENT_DATE |/" /tmp/ISSUE-BODY.md
    fi

    if ! diff -q /tmp/ISSUE-BODY.md /tmp/ISSUE-BODY.md.original; then
        echo "Update issue $issue_number with new release information."
        gh issue edit $issue_number --body-file /tmp/ISSUE-BODY.md
    fi

done
