#!/bin/bash
set -euo pipefail

echo "🔍 Testing vips-modules symlink version consistency"

SNAPCRAFT_YAML="${SNAPCRAFT_YAML:-../snap/snapcraft.yaml}"
APTLY_REPO="https://nsg.github.io/aptly/"

if [ ! -f "$SNAPCRAFT_YAML" ]; then
    echo "❌ Error: snapcraft.yaml not found at $SNAPCRAFT_YAML"
    exit 1
fi

echo "📄 Using snapcraft.yaml: $SNAPCRAFT_YAML"

echo "📋 Extracting vips-modules symlink from snapcraft.yaml..."
SYMLINK_PATH=$(grep "/usr/lib/vips-modules" "$SNAPCRAFT_YAML" | head -1 | sed 's/.*vips-modules-//' | sed 's/:.*//')

if [ -z "$SYMLINK_PATH" ]; then
    echo "❌ Error: Could not find vips-modules symlink in snapcraft.yaml"
    exit 1
fi

echo "   Found: vips-modules-$SYMLINK_PATH"

echo "🌐 Fetching nsg-libvips package version from aptly repository..."
LIBVIPS_VERSION=$(curl -s "$APTLY_REPO" | grep -oP 'nsg-libvips-\K[0-9]+\.[0-9]+\.[0-9]+' | head -1)

if [ -z "$LIBVIPS_VERSION" ]; then
    echo "❌ Error: Could not fetch libvips version from $APTLY_REPO"
    exit 1
fi

echo "   Found: libvips $LIBVIPS_VERSION"

MAJOR_MINOR=$(echo "$LIBVIPS_VERSION" | cut -d. -f1-2)
echo "   Expected vips-modules version: $MAJOR_MINOR"

if [ "$SYMLINK_PATH" = "$MAJOR_MINOR" ]; then
    echo "✅ Success: vips-modules symlink ($SYMLINK_PATH) matches libvips version ($MAJOR_MINOR)"
    exit 0
else
    echo "❌ Error: Version mismatch!"
    echo "   vips-modules symlink points to: $SYMLINK_PATH"
    echo "   libvips package version:        $MAJOR_MINOR"
    echo ""
    echo "   Fix: Update snap/snapcraft.yaml to use:"
    echo "     /usr/lib/vips-modules-$MAJOR_MINOR:"
    echo "       symlink: \$SNAP/usr/lib/vips-modules-$MAJOR_MINOR"
    exit 1
fi
