#!/bin/bash

set -o pipefail -eu

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)

for test in ${SCRIPT_DIR}/test_*.sh; do
    if $test; then
        echo -e "✨ \e[1m$(basename $test)\e[0m \t✅ Test OK"
    else
        echo -e "✨ \e[1m$(basename $test)\e[0m \t🔴 Test failed"
        exit 1
    fi
done
