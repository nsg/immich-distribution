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

if ! [[ "$NEW_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Version $NEW_VERSION is not a valid version number."
    exit 1
fi

if [ "$OLD_VERSION" == "$NEW_VERSION" ]; then
    echo "No version update detected."
    exit 0
fi

if git ls-remote --exit-code "$REMOTE_URL" "refs/heads/$BRANCH_NAME" >/dev/null 2>&1; then
    echo "Branch $BRANCH_NAME already exists."
    exit 0
fi

echo "
Tracking issue for Immich $NEW_VERSION.
" > /tmp/ISSUE-BODY.md

if get_issue_number "${NEW_VERSION_MAJOR_MINOR:1}" | grep -qE '.'; then
    echo "Issue for $NEW_VERSION_MAJOR_MINOR already exists."
else
    gh issue create \
        --title "Immich $NEW_VERSION_MAJOR_MINOR released" \
        --label new-version \
        --body-file /tmp/ISSUE-BODY.md
fi

git checkout -b $BRANCH_NAME
git add .
git commit -m "Bump version to $NEW_VERSION"
git push -u origin $BRANCH_NAME

echo "
This PR bumps the version from **$OLD_VERSION** to **$NEW_VERSION**.
Please review the changes and merge this PR if everything looks good.

## Version update output
$(cat /tmp/version-update)

## Upstream release notes
https://github.com/immich-app/immich/releases/tag/$NEW_VERSION

## Monitored upstream files
$(./update.sh $OLD_VERSION $NEW_VERSION)

## Checklist
* Review the changes above
* Possible write a news entry (and push it to this PR)
* Wait for the CI to finish
* Merge the PR
" | gh pr create --base master --assignee=nsg --title "Bump $NEW_VERSION" --body-file -
