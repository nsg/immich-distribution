#!/bin/bash
set -eo pipefail

#
# Create a version bump PR for the newest minor on the oldest open tracking issue
#

. workflows/tools.sh

REMOTE_URL=$(git remote get-url origin)

# Oldest tracking issue (lowest issue number)
TRACKING_ISSUE="$(list_tracking_issues | sort -n | head -n 1)"

if [ -z "$TRACKING_ISSUE" ]; then
    echo "No tracking issue found."
    exit 0
fi

TRACKING_ISSUE_TITLE="$(get_issue_title $TRACKING_ISSUE)"
TRACKING_ISSUE_VERSION_MAJOR_MINOR="$(echo $TRACKING_ISSUE_TITLE | awk '{ print $2 }')"

# Fetch versions (old and new)
OLD_VERSION=$(cat VERSION)
NEW_VERSION=$(get_latest_release_for_major_minor $TRACKING_ISSUE_VERSION_MAJOR_MINOR)
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

git checkout -b $BRANCH_NAME

# Bump version
sed -i "s/$OLD_VERSION/$NEW_VERSION/g" snap/snapcraft.yaml
sed -i "s/$OLD_VERSION/$NEW_VERSION/g" parts/machine-learning/Makefile
sed -i "s/$OLD_VERSION/$NEW_VERSION/g" patches/Makefile
sed -i "s/$OLD_VERSION/$NEW_VERSION/g" VERSION

git add .
git commit -m "Bump version to $NEW_VERSION"

# Push to GitHub via SSH to trigger the GitHub Action Events
git push -u origin $BRANCH_NAME --repo=ssh://git@github.com:nsg/immich-distribution.git

echo "
This PR bumps the version from **$OLD_VERSION** to **$NEW_VERSION**.
Please review the changes and merge this PR if everything looks good.

## Version update output
$(cat /tmp/version-update)

## New immich-cli version
$(new_cli_version)

## Upstream release notes
* https://github.com/immich-app/immich/releases/tag/$NEW_VERSION

## Monitored upstream files
$(./update.sh $OLD_VERSION $NEW_VERSION)

## Checklist
* Review the changes above
* Possible write a news entry (and push it to this PR)
* Wait for the CI to finish
* Merge the PR

ref #${TRACKING_ISSUE}
" | create_pr

