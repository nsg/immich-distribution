#!/bin/bash

latest_version=$(curl -s https://api.github.com/repos/immich-app/immich/releases/latest | jq -r '.tag_name')
current_version="$(cat VERSION)"

echo "OLD: $current_version"
echo "NEW: $latest_version"

sed -i "s/$current_version/$latest_version/g" snap/snapcraft.yaml
sed -i "s/$current_version/$latest_version/g" parts/machine-learning/Makefile
sed -i "s/$current_version/$latest_version/g" patches/Makefile
sed -i "s/$current_version/$latest_version/g" VERSION

latest_immich_cli_version=$(curl -s https://api.github.com/repos/immich-app/CLI/releases/latest | jq -r '.tag_name')
if ! grep -q $latest_immich_cli_version snap/snapcraft.yaml; then
    echo "Note, new immich-cli version available: $latest_immich_cli_version"
fi
