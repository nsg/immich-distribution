#!/bin/bash
set -eo pipefail

# This script is triggered by a GitHub Action in the Auto Bump workflow.

OLD_VERSION=$(cat VERSION)
make version-update > /tmp/version-update 2>&1
NEW_VERSION=$(cat VERSION)
BRANCH_NAME="bump-$NEW_VERSION"
REMOTE_URL=$(git remote get-url origin)
NEW_VERSION_MAJOR_MINOR=$(echo $NEW_VERSION | cut -d. -f1-2)

get_issue_number() {
    gh issue list \
        --label new-version \
        --state open \
        --search "Immich $1 released" \
        --json number \
        --limit 1 \
        --jq ".[].number"
}

get_pr_number() {
    gh pr list \
        --state open \
        --search "Bump $1" \
        --json number \
        --limit 1 \
        --jq ".[].number"
}

has_any_pr_bump_open() {
    get_pr_number | grep -qE '.'
}

create_pr() {
    gh pr create --base master --assignee=nsg --title "Bump $NEW_VERSION" --body-file -
}

new_cli_version() {
    latest_immich_cli_version=$(curl -s https://api.github.com/repos/immich-app/CLI/releases/latest | jq -r '.tag_name')
    if grep -q $latest_immich_cli_version snap/snapcraft.yaml; then
        echo "No new immich-cli version available."
    else
        echo "Note, new immich-cli version available: $latest_immich_cli_version"
    fi
}

#
# No nothing or fail if these checks conditions are met
#

if ! [[ "$NEW_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Version $NEW_VERSION is not a valid version number."
    exit 1
fi

if [ "$OLD_VERSION" == "$NEW_VERSION" ]; then
    echo "No version update detected."
    exit 0
fi

#
# Setup and tracking issue for the new version, unless already there
#

echo "
A new version of Immich has been released. :tada:

This issue has been created to track the release of Immich **$NEW_VERSION_MAJOR_MINOR**.
Feel free to add any comments or questions related to the release here.

## Upstream release notes
* https://github.com/immich-app/immich/releases/tag/$NEW_VERSION
* https://github.com/immich-app/immich/releases

## When will this be released?
Expect it to be released in the next few days to the beta channel, and to stable a few days later.
It may be faster if there are no issues with the release.
" > /tmp/ISSUE-BODY.md

if get_issue_number "${NEW_VERSION_MAJOR_MINOR}" | grep -qE '.'; then
    echo "Issue for $NEW_VERSION_MAJOR_MINOR already exists."
else
    gh issue create \
        --title "Immich $NEW_VERSION_MAJOR_MINOR released" \
        --label new-version \
        --body-file /tmp/ISSUE-BODY.md
fi

#
# Create a branch and PR for the new version, unless already there
#

if has_any_pr_bump_open; then
    echo "There is already a PR open to bump a version."
    echo "This script will wait for that PR to be merged before creating a new one for $NEW_VERSION."
    exit 0
fi

if git ls-remote --exit-code "$REMOTE_URL" "refs/heads/$BRANCH_NAME" >/dev/null 2>&1; then
    echo "Branch $BRANCH_NAME already exists."
    exit 0
fi

git checkout -b $BRANCH_NAME
git add .
git commit -m "Bump version to $NEW_VERSION"

# Push to GitHub via SSH to trigger the GitHub Action Events
git push -u origin $BRANCH_NAME --repo=git@github.com:nsg/immich-distribution.git

echo "
This PR bumps the version from **$OLD_VERSION** to **$NEW_VERSION**.
Please review the changes and merge this PR if everything looks good.

## Version update output
$(cat /tmp/version-update)

## New immich-cli version
$(new_cli_version)

## Upstream release notes
https://github.com/immich-app/immich/releases/tag/$NEW_VERSION

## Monitored upstream files
$(./update.sh $OLD_VERSION $NEW_VERSION)

## Checklist
* Review the changes above
* Possible write a news entry (and push it to this PR)
* Wait for the CI to finish
* Merge the PR

ref #$(get_issue_number "${NEW_VERSION_MAJOR_MINOR}")
" | create_pr
