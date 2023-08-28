#!/bin/bash

get_stats() {
    curl -s 'http://localhost/haproxy/;csv'
}

backends_down() {
    echo -n "[$N/$MAX] Backends DOWN: "
    get_stats | awk -F, '/BACKEND.*DOWN/{ print $1 }' | tr '\n' ' '
    echo
}

is_backend_down() {
    get_stats | awk -F, '/BACKEND/{ print $18 }' | uniq | grep -q DOWN
}

systemd_units() {
    systemctl list-units snap.immich-distribution.*.service --full --all --output json --no-pager | jq -r '.[].unit'
}

systemd_status_success() {
    systemctl show -p ExecMainStatus "$1" | grep -q "ExecMainStatus=0"
}

log() {
    echo
    echo "###"
    echo "$@"
    echo "###"
    echo
}

N=0
MAX=60
while is_backend_down; do
    backends_down

    if [ "$N" -ge "$MAX" ]; then
        echo "ERROR: Backends are still DOWN after $MAX seconds"
        log "Failed units"
        for unit in $(systemd_units); do
            echo "Unit: $unit"
            systemd_status_success "$unit" || systemctl status "$unit"

        done
        log "Last 100 lines of log"
        journalctl -n 100 -eu snap.immich-distribution.*
        exit 1
    fi

    sleep 1
    N=$((N+1))
done
