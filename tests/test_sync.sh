#!/bin/bash

CGROUP_NAME="snap.immich-distribution.sync-service.service"
INITIAL_NUMBER_OF_ASSETS=${EXPECTED_INITIAL_IMAGE_COUNT:-25}

log() {
    echo -e "🎲 $@"
}

die() {
    echo "💥 $@" >&2
    exit 1
}

reset_sync_service() {
    sudo snap unset immich-distribution sync-enabled
    sudo snap unset immich-distribution sync-delete-threshold
    sudo snap unset immich-distribution sync
}

get_secret() {
    cat secret.txt
}

get_headers() {
    echo "Accept: application/json"
    echo "X-API-KEY: $(get_secret)"
}

get_ip_address() {
    ip route get 8.8.8.8 | grep -oP 'src \K[^ ]+'
}

get_number_of_assets() {
    local ip=$(get_ip_address)
    local response=$(curl -s "http://${ip}/api/server/statistics" -H "$(get_headers)")
    local photos=$(echo "$response" | jq -r '.photos')
    local videos=$(echo "$response" | jq -r '.videos')
    echo $((photos + videos))
}

get_user_id() {
    local ip=$(get_ip_address)
    local response=$(curl -s "http://${ip}/api/users/me" -H "$(get_headers)")
    echo "$response" | jq -r '.id'
}

get_asset_id() {
    local filename=$1
    local ip=$(get_ip_address)
    local response=$(curl -s "http://${ip}/api/search/metadata" \
        -H "$(get_headers)" \
        -H "Content-Type: application/json" \
        -d "{\"originalFileName\": \"${filename}\"}")
    echo "$response" | jq -r '.assets.items[0].id'
}

delete_asset() {
    local asset_id=$1
    local ip=$(get_ip_address)
    curl -s -X DELETE "http://${ip}/api/assets" \
        -H "$(get_headers)" \
        -H "Content-Type: application/json" \
        -d "{\"ids\": [\"${asset_id}\"]}" \
        -w "%{http_code}" | grep -q "204" || die "Failed to delete asset ${asset_id}"
}

empty_trash() {
    local ip=$(get_ip_address)
    curl -s -X POST "http://${ip}/api/trash/empty" \
        -H "$(get_headers)" \
        -w "%{http_code}" | grep -q "200" || die "Failed to empty trash"
}

processes_in_cgroup() {
    systemd-cgls --full --no-pager -u "$CGROUP_NAME" 2>/dev/null
}

get_sync_service_journal_messages() {
    journalctl --no-pager -n 25 -e -u snap.immich-distribution.sync-service.service
}

get_sync_service_status() {
    local output=$(systemctl show snap.immich-distribution.sync-service.service -p ExecMainStatus)
    echo "${output#*=}"
}

wait_for_asset_count() {
    local expected=$1
    local timeout=60
    local interval=2

    echo -n "Waiting for assets to be $expected... "
    for ((i=0; i<timeout; i+=interval)); do
        local current=$(get_number_of_assets)
        echo -ne "\rWaiting for assets to be $expected ($current) [${i}/${timeout}]"
        if [[ $current -eq $expected ]]; then
            echo
            return 0
        fi
        sleep $interval
    done
    echo -e "\rWaiting for assets to be $expected... [${timeout}/${timeout}]"
    return 1
}

add_file() {
    cp -v "test-assets/albums/nature/$1" \
   "/var/snap/immich-distribution/common/sync/$(get_user_id)/$1"
}

remove_file() {
    rm -v "/var/snap/immich-distribution/common/sync/$(get_user_id)/$1"
}

if [[ "$CI" != "true" ]]; then
    log "Reset the sync service to a clean state"
    reset_sync_service
fi

./test_haproxy.sh

log "Make sure that the sync service is not running"
if processes_in_cgroup | grep -qE 'python3'; then
    die "Sync service is running, but is should be disabled on a new installation."
fi

log "Make sure that the the number of assets is the expected value of $INITIAL_NUMBER_OF_ASSETS"
if ! wait_for_asset_count $INITIAL_NUMBER_OF_ASSETS; then
    die "Expected the number of assets to be $INITIAL_NUMBER_OF_ASSETS within 1 minute, but it was not."
fi

log "Enable the sync service, no keys are provided so the service should not start."
sudo snap set immich-distribution sync-enabled=true
./test_haproxy.sh

log "Verify that the database is modified as expected."
sleep 10
output=$(get_sync_service_journal_messages)

if ! echo "$output" | grep -q "CREATE TABLE"; then
    die "Expected to find 'CREATE TABLE' in service logs"
fi

if ! echo "$output" | grep -q "CREATE FUNCTION"; then
    die "Expected to find 'CREATE FUNCTION' in service logs"
fi

if ! echo "$output" | grep -q "CREATE TRIGGER"; then
    die "Expected to find 'CREATE TRIGGER' in service logs"
fi

log "Verify that the service exited with a zero exit code."
if [[ $(get_sync_service_status) -ne 0 ]]; then
    die "Service exited with a non-zero exit code."
fi

log "Enable sync service and provide a key"
sudo snap set immich-distribution sync="$(get_secret)"
./test_haproxy.sh
sudo chmod -R 777 /var/snap/immich-distribution/common/sync

log "Make sure that the sync service is running"
sleep 30
if ! processes_in_cgroup | grep -qE 'python3'; then
    die "Sync service is not running, but it should be."
fi

log "Add file polemonium_reptans.jpg"
add_file "polemonium_reptans.jpg"

log "Verify that the file is added to Immich via the API."
sleep 10
if ! wait_for_asset_count $((INITIAL_NUMBER_OF_ASSETS + 1)); then
    die "Expected the number of assets to increase to $((INITIAL_NUMBER_OF_ASSETS + 1)) within 1 minute, but it did not."
fi

log "Remove the file polemonium_reptans.jpg"
remove_file "polemonium_reptans.jpg"

log "Verify that the file is removed from Immich via the API."
sleep 10
if ! wait_for_asset_count $INITIAL_NUMBER_OF_ASSETS; then
    die "Expected the number of assets to decrease to $INITIAL_NUMBER_OF_ASSETS within 1 minute, but it did not."
fi

log "Set delete threshold to 0 days"
sudo snap set immich-distribution sync-delete-threshold=0
./test_haproxy.sh
sleep 10

log "Add file cyclamen_persicum.jpg"
add_file "cyclamen_persicum.jpg"

log "Verify that the file is added to Immich via the API."
sleep 10
if ! wait_for_asset_count $((INITIAL_NUMBER_OF_ASSETS + 1)); then
    die "Expected the number of assets to increase to $((INITIAL_NUMBER_OF_ASSETS + 1)) within 1 minute, but it did not."
fi

log "Remove the file cyclamen_persicum.jpg"
remove_file "cyclamen_persicum.jpg"

log "Verify that the file is still in Immich via the API."
sleep 10
if ! wait_for_asset_count $((INITIAL_NUMBER_OF_ASSETS + 1)); then
    die "Expected the number of assets to stay the same"
fi

log "Add file tanners_ridge.jpg"
add_file "tanners_ridge.jpg"

log "Verify that the file is added to Immich via the API."
sleep 10
if ! wait_for_asset_count $((INITIAL_NUMBER_OF_ASSETS + 2)); then
    die "Expected the number of assets to increase"
fi

log "Delete the asset from Immich via the API."
asset_id=$(get_asset_id "tanners_ridge.jpg")
delete_asset "$asset_id"
sleep 10
empty_trash
sleep 30

log "Verify that the file is removed from the watch folder."
if [[ -f "/var/snap/immich-distribution/common/sync/$(get_user_id)/tanners_ridge.jpg" ]]; then
    die "File tanners_ridge.jpg was not removed from the watch folder after 30 seconds."
fi
