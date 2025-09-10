#!/bin/bash

#
# Test Immich built in backup functionality
# This test depends on the development build being installed and the prep tests having run
#

log() {
    echo -e "🔧 BACKUP TEST: $*"
}

die() {
    echo "💥 BACKUP TEST FAILED: $*" >&2
    exit 1
}

get_ip_address() {
    ip route get 8.8.8.8 | grep -oP 'src \K[^ ]+'
}

get_api_key() {
    if [ -f "secret.txt" ]; then
        cat secret.txt
    else
        die "API key file secret.txt not found. Run prep tests first."
    fi
}

# Main test execution
log "Starting built-in Immich database backup test"

ip=$(get_ip_address)
api_key=$(get_api_key)
immich_backup_dir="/var/snap/immich-distribution/common/upload/backups"

sudo mkdir -p "$immich_backup_dir"

journal_cursor=$(journalctl --show-cursor -n 0 2>/dev/null | grep -o 'cursor: .*' | cut -d' ' -f2)

log "Triggering database backup via Immich API..."

# Trigger backup using the Immich API
response=$(curl -s -w "%{http_code}" \
    -X POST "http://${ip}/api/jobs" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "X-API-KEY: $api_key" \
    -d '{"name": "backup-database"}')

http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" != "204" ] && [ "$http_code" != "201" ] && [ "$http_code" != "200" ]; then
    log "API response: HTTP $http_code - Body: $body"
    die "Backup API request failed with HTTP $http_code"
fi

log "Backup API request successful (HTTP $http_code)"

log "Waiting 30 seconds for backup to complete..."
sleep 30

backup_file=$(sudo find "$immich_backup_dir" -name "immich-db-backup-*.sql.gz" -type f 2>/dev/null | head -n1)

if [ -z "$backup_file" ]; then
    log "Available files in backup directory:"
    sudo ls -la "$immich_backup_dir" || true
    die "Backup file not found in $immich_backup_dir after waiting"
fi

log "Backup file found: $backup_file"

log "Checking journal logs for errors..."
error_patterns="ERROR|Failed|failed|Error|error"
journal_errors=$(journalctl --after-cursor="$journal_cursor" -u snap.immich-distribution.* 2>/dev/null | grep -E "$error_patterns" || true)

if [ -n "$journal_errors" ]; then
    log "Found errors in journal logs:"
    echo "$journal_errors"
    die "Backup process generated errors in the journal"
fi

log "No errors found in journal logs"

if [ ! -s "$backup_file" ]; then
    die "Backup file is empty or does not exist"
fi

log "Verifying backup file integrity"

if ! sudo zcat "$backup_file" | head -n 10 | grep -q "PostgreSQL"; then
    die "Backup file appears to be invalid - missing PostgreSQL header"
fi

log "Built-in Immich database backup test completed successfully! ✅"
