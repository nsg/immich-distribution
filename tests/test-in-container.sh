#!/bin/bash
set -e

UBUNTU_VERSION="22.04"

function show_help {
    cat << EOF
Usage: $(basename "$0") COMMAND [ARGS...]

Run commands in Ubuntu 22.04 container to test package compatibility.
This ensures compatibility with core22 snap base.

The container has apt repositories available and can install packages.

EXAMPLES:
    # Check if package exists and show version
    $(basename "$0") apt-cache show libgl1

    # Install package and list its files
    $(basename "$0") apt-get install -y libgl1 '&&' dpkg -L libgl1

    # Test Python package import
    $(basename "$0") apt-get install -y python3-pip libgl1 '&&' pip3 install rapidocr '&&' python3 -c "'import rapidocr'"

    # Check library dependencies
    $(basename "$0") apt-get install -y libgl1 '&&' dpkg -L libgl1 '|' grep .so

NOTE:
    - Commands run in a fresh container each time
    - Use quotes around shell operators like '&&', '|', '>'
    - The container runs with 'bash -c', so shell syntax works
    
EOF
}

if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

echo "Running in Ubuntu $UBUNTU_VERSION container..."
echo ""

podman run --rm ubuntu:$UBUNTU_VERSION bash -c "apt-get update -qq > /dev/null 2>&1 && $*"
