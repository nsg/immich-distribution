#!/bin/bash
# View release notes from immich-app/immich repository
# Usage: ./tests/view-release-notes.sh <version> [--search <term>]

set -e

VERSION="$1"
SEARCH_TERM=""

if [[ -z "$VERSION" ]]; then
    echo "Usage: $0 <version> [--search <term>]" >&2
    echo "Example: $0 v2.2.0" >&2
    echo "Example: $0 v2.2.0 --search breaking" >&2
    exit 1
fi

if [[ "$2" == "--search" && -n "$3" ]]; then
    SEARCH_TERM="$3"
fi

if [[ -n "$SEARCH_TERM" ]]; then
    gh release view "$VERSION" --repo immich-app/immich --json body --jq .body | grep -i "$SEARCH_TERM"
else
    gh release view "$VERSION" --repo immich-app/immich
fi
