#!/bin/bash

#
# This tool diffs a few files to detect changes in the upstream images and scripts
#

REPO_PATH="https://github.com/immich-app/immich.git"
TMPDIR="$(mktemp -d)"

set -eo pipefail

if [ -d "$TMPDIR" ]; then
    trap "rm -rf $TMPDIR; echo \"$TMPDIR removed\"" EXIT
fi

vdiff() {
    if [ -z $GITHUB_ACTIONS ]; then
        COLOR=always
    else
        COLOR=never
    fi
    echo '```diff'
    git diff --color=$COLOR -w $OLD_RELEASE_TAG $NEW_RELEASE_TAG -- $1
    echo '```'
}

git clone $REPO_PATH $TMPDIR

if [ -e $1 ]; then
    OLD_RELEASE_TAG="$(grep -A4 '  server:' snap/snapcraft.yaml | awk '/source-tag/{ print $2 }')"
    echo "Old release selected as: $OLD_RELEASE_TAG"
else
    OLD_RELEASE_TAG="$1"
fi

cd $TMPDIR

if [ -z $2 ]; then
    NEW_RELEASE_TAG="$(git tag --sort=committerdate | tail -1)"
    echo "New release selected as: $NEW_RELEASE_TAG"
else
    NEW_RELEASE_TAG="$2"
fi

# Check out the new release
git checkout $NEW_RELEASE_TAG

CHECK_FILES="
    server/src/migrations
    server/Dockerfile
    server/start.sh
    web/README.md
    web/Dockerfile
    web/src/lib/components/shared-components/version-announcement-box.svelte
    cli/README.md
    machine-learning/README.md
    machine-learning/Dockerfile
    machine-learning/start.sh
    machine-learning/gunicorn_conf.py
    docker/example.env
    docker/docker-compose.yml
    docs/docs/install/environment-variables.md
    docs/docs/features/command-line-interface.md
"

for F in $CHECK_FILES; do
    if [ ! -e "$F" ]; then
        echo "Error, $F do not exists"
    else
        vdiff "$F"
    fi
done | less -R

cd -
if grep -q $OLD_RELEASE_TAG snap/snapcraft.yaml; then
    echo
    echo "Found the string $OLD_RELEASE_TAG in snapcraft.yaml"
    echo
fi

if ! grep -q $NEW_RELEASE_TAG snap/snapcraft.yaml; then
    echo
    echo "The string $NEW_RELEASE_TAG was NOT found in snapcraft.yaml"
    echo
fi
