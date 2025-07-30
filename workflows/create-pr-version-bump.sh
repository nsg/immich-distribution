#!/bin/bash
set -eo pipefail

#
# Create a version bump PR for the newest minor on the oldest open tracking issue
#

. workflows/tools.sh

REMOTE_URL=$(git remote get-url origin)
OLD_VERSION=$(cat VERSION)

#
# By default, use the oldest open tracking issues latest release as the new version
# Unless the latest release is already in the VERSION file, then use the next tracking issue
#

for n in $(list_tracking_issues | sort -n); do
    TRACKING_ISSUE_TITLE="$(get_issue_title $n)"
    TRACKING_ISSUE_VERSION_MAJOR_MINOR="$(echo $TRACKING_ISSUE_TITLE | awk '{ print $2 }')"
    NEW_VERSION=$(get_latest_release_for_major_minor $TRACKING_ISSUE_VERSION_MAJOR_MINOR)
    if [[ $(version_to_int "$NEW_VERSION") -gt $(version_to_int "$OLD_VERSION") ]]; then
        TRACKING_ISSUE=$n
        break
    fi
done

if [ -z "$TRACKING_ISSUE" ]; then
    echo "No tracking issue found."
    exit 0
fi

BRANCH_NAME="bump/$NEW_VERSION"

if has_any_pr_bump_open; then
    echo "There is already a PR open to bump a version."
    echo "This script will wait for that PR to be merged before creating a new one."
    exit 0
fi

if git ls-remote --exit-code "$REMOTE_URL" "refs/heads/$BRANCH_NAME" >/dev/null 2>&1; then
    echo "Branch $BRANCH_NAME already exists."
    exit 0
fi

if [[ $(version_to_int "$NEW_VERSION") -lt $(version_to_int "$OLD_VERSION") ]]; then
    echo "New version $NEW_VERSION is older then old version $OLD_VERSION, abort execution"
    exit 0
fi

git checkout -b $BRANCH_NAME

# Bump version
sed -i "s/$OLD_VERSION/$NEW_VERSION/g" snap/snapcraft.yaml
sed -i "s/$OLD_VERSION/$NEW_VERSION/g" VERSION

git add .
git commit -m "Bump version to $NEW_VERSION"

# Push to GitHub via SSH to trigger the GitHub Action Events
git push -u origin $BRANCH_NAME --repo=ssh://git@github.com:nsg/immich-distribution.git

echo "
This PR bumps the version from **$OLD_VERSION** to **$NEW_VERSION**.
Please review the changes and merge this PR if everything looks good.

## Upstream release notes
* https://github.com/immich-app/immich/releases/tag/$NEW_VERSION

## Monitored upstream files
$(./update.sh $OLD_VERSION $NEW_VERSION)

## Base image
Check the base images for recent relevant changes:

* https://github.com/immich-app/base-images/commits/main/

## Checklist
* Review the changes above
* Possible write a news entry (and push it to this PR)
* Wait for the CI to finish
* Merge the PR

ref #${TRACKING_ISSUE}
" | create_pr

