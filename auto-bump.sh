#!/bin/bash
set -eo pipefail

# This script is triggered by a GitHub Action in the Auto Bump workflow.

OLD_VERSION=$(cat VERSION)
make version-update > /tmp/version-update 2>&1
NEW_VERSION=$(cat VERSION)
BRANCH_NAME="bump/$NEW_VERSION"
REMOTE_URL=$(git remote get-url origin)
NEW_VERSION_MAJOR_MINOR=$(echo $NEW_VERSION | cut -d. -f1-2)

get_issue_number() {
    gh issue list \
        --label new-version \
        --state open \
        --search "Immich $1 released" \
        --json number \
        --limit 1 \
        --jq ".[].number" 2>/dev/null
}

get_pr_number() {
    gh pr list \
        --state open \
        --search "Bump $1" \
        --json number \
        --limit 1 \
        --jq ".[].number" 2>/dev/null
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

snapstore_version() {
    snap info immich-distribution | awk "/^ *latest\/$1/{ print \$2 }" | cut -d'-' -f1
}

#
# No nothing or fail if these checks conditions are met
#

if ! [[ "$NEW_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Version $NEW_VERSION is not a valid version number."
    exit 1
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

## Channels

| Name | Version | Released | Note |
| ---- | ------- | -------- | ---- |
| Edge | <TBD-E> | | Development builds |
| Beta | <TBD-B> | | Released for testing |
| Candidate | <TDB-C> | | Release candidate / deployed on a live system |
| Stable | <TBD-S> | | Released :tada:  |
" > /tmp/ISSUE-BODY.md

ISSUE_NUMBER="$(get_issue_number "${NEW_VERSION_MAJOR_MINOR}")"
if [ ! -z $ISSUE_NUMBER ]; then
    echo "Issue for $NEW_VERSION_MAJOR_MINOR already exists, issue $ISSUE_NUMBER."

    # Export the issue body to a file
    gh issue view $ISSUE_NUMBER --json body --jq ".body" > /tmp/ISSUE-BODY.md
    cp /tmp/ISSUE-BODY.md /tmp/ISSUE-BODY.md.original

    if grep -qE "https.*releases\/tag\/$NEW_VERSION" /tmp/ISSUE-BODY.md; then
        echo "Release link for $NEW_VERSION already exists."
    else
        sed -i "/https.*releases\/tag\/v.*/a * https://github.com/immich-app/immich/releases/tag/$NEW_VERSION" /tmp/ISSUE-BODY.md
        gh issue edit $ISSUE_NUMBER --body-file /tmp/ISSUE-BODY.md
    fi

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
        echo "Update issue $ISSUE_NUMBER with new release information."
        gh issue edit $ISSUE_NUMBER --body-file /tmp/ISSUE-BODY.md
    fi

else
    gh issue create \
        --title "Immich $NEW_VERSION_MAJOR_MINOR released" \
        --label new-version \
        --body-file /tmp/ISSUE-BODY.md
fi

#
# Skip PR creation if there is no new version
#

if [ "$OLD_VERSION" == "$NEW_VERSION" ]; then
    echo "No version update detected, no pull request will be created."
    exit 0
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

ref #$(get_issue_number "${NEW_VERSION_MAJOR_MINOR}")
" | create_pr

