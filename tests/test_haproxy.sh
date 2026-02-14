#!/bin/bash

HAPROXY_STATS_URL='http://localhost/haproxy/;csv'

get_stats() {
    curl -s "$HAPROXY_STATS_URL"
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

while ! curl -s -o /dev/null "$HAPROXY_STATS_URL"; do
    echo "Waiting for haproxy stats..."
    sleep 1
done

N=0
MAX=240
while is_backend_down; do
    backends_down | tr '\n' '\r'

    if [ "$N" -ge "$MAX" ]; then
        echo "ERROR: Backends are still DOWN after $MAX seconds"
        log "Unit status summary"
        failed_units=""
        for unit in $(systemd_units); do
            if systemd_status_success "$unit"; then
                echo "  OK:   $unit"
            else
                echo "  FAIL: $unit"
                failed_units="$failed_units $unit"
            fi
        done

        for unit in $failed_units; do
            log "Journal for $unit"
            journalctl -n 100 -eu "$unit" --no-pager
        done
        exit 1
    fi

    sleep 1
    N=$((N+1))
done
