#!/bin/bash

#
# This tool diffs a few files to detect changes in the upstream images and scripts
#

REPO_PATH="https://github.com/immich-app/immich.git"
TMPDIR="$(mktemp -d)"

if [ -d "$TMPDIR" ]; then
    trap "rm -rf $TMPDIR; echo \"$TMPDIR removed\"" EXIT
fi

vdiff() {
    git diff -w $OLD_RELEASE_TAG $NEW_RELEASE_TAG -- $1
}

git clone $REPO_PATH $TMPDIR
cd $TMPDIR

OLD_RELEASE_TAG="$1"

if [ -z $2 ]; then
    NEW_RELEASE_TAG="$(git tag --sort=committerdate | tail -1)"
else
    NEW_RELEASE_TAG="$2"
fi

CHECK_FILES="
    server/Dockerfile
    server/start-server.sh
    server/start-microservices.sh
    server/README.md
    web/README.md
    web/entrypoint.sh
    web/Dockerfile
    web/src/lib/components/shared-components/version-announcement-box.svelte
    nginx
    machine-learning/README.md
    machine-learning/Dockerfile
    docker/example.env
    docker/docker-compose.yml
"

for F in $CHECK_FILES; do
    if [ ! -e "$F" ]; then
        echo "Error, $F do not exists"
        exit 1
    fi
done

for F in $CHECK_FILES; do
    vdiff "$F"
done

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
