#!/bin/bash

latest_version=$(curl -s https://api.github.com/repos/immich-app/immich/releases/latest | jq -r '.tag_name')
current_version=$(snap info immich-distribution | grep stable | awk '{print $2}')
current_version=${current_version%-*}

echo "OLD: $current_version"
echo "NEW: $latest_version"

sed -i "s/$current_version/$latest_version/g" snap/snapcraft.yaml
sed -i "s/$current_version/$latest_version/g" parts/machine-learning/Makefile
sed -i "s/$current_version/$latest_version/g" patches/Makefile
