#!/bin/bash

set -euo pipefail

#
# Test metrics endpoints
#
# Validates that Prometheus metrics work when enabled via snap configuration.
# Tests both API (port 8081) and Microservices (port 8082) metrics endpoints,
# and verifies that include/exclude settings change the exported metric families.
#

SNAP_NAME="immich-distribution"
TEST_DIR="$(dirname "$0")"
METRICS_API_URL="http://127.0.0.1:8081/metrics"
METRICS_MICROSERVICES_URL="http://127.0.0.1:8082/metrics"

TMPDIR_METRICS="$(mktemp -d)"
ALL_API_METRIC_NAMES="$TMPDIR_METRICS/all_api_metrics.txt"
API_ONLY_METRIC_NAMES="$TMPDIR_METRICS/api_only_metrics.txt"
ALL_EXCEPT_API_METRIC_NAMES="$TMPDIR_METRICS/all_except_api_metrics.txt"

log() {
    echo -e "📊 METRICS TEST: $@"
}

die() {
    echo "💥 METRICS TEST FAILED: $@" >&2
    exit 1
}

set_snap_value() {
    local key="$1"
    local value="$2"

    if [ -n "$value" ]; then
        sudo snap set "$SNAP_NAME" "$key=$value"
    else
        sudo snap unset "$SNAP_NAME" "$key"
    fi
}

restart_and_wait() {
    sudo snap restart "$SNAP_NAME"
    make wait -C "$TEST_DIR"
}

apply_metrics_config() {
    local include="$1"
    local exclude="$2"

    set_snap_value metrics-telemetry-include "$include"
    set_snap_value metrics-telemetry-exclude "$exclude"
    restart_and_wait
}

http_code() {
    local url="$1"

    curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || true
}

wait_for_metrics() {
    local url="$1"
    local name="$2"
    local max=60
    local n=0
    local response=""

    while [ "$n" -lt "$max" ]; do
        response=$(http_code "$url")
        if [ "$response" = "200" ]; then
            return 0
        fi
        sleep 1
        n=$((n+1))
    done

    die "$name metrics endpoint did not return 200 after ${max}s (last HTTP status: $response)"
}

metric_names_to_file() {
    local body="$1"
    local output="$2"

    awk '
        /^[#]/ { next }
        NF == 0 { next }
        {
            split($1, parts, "{")
            name = parts[1]
            sub(/_bucket$/, "", name)
            sub(/_sum$/, "", name)
            sub(/_count$/, "", name)
            print name
        }
    ' <<< "$body" | sort -u > "$output"

    if [ ! -s "$output" ]; then
        die "Failed to extract metric names from Prometheus output"
    fi
}

# Test 1: Metrics should not be available by default
log "Test 1: Verify metrics are disabled by default"

api_status=$(http_code "$METRICS_API_URL")
if [ "$api_status" = "200" ]; then
    die "API metrics endpoint returned 200 when metrics should be disabled"
fi

microservices_status=$(http_code "$METRICS_MICROSERVICES_URL")
if [ "$microservices_status" = "200" ]; then
    die "Microservices metrics endpoint returned 200 when metrics should be disabled"
fi

log "Metrics disabled by default - OK"

# Test 2: Enable all metrics and verify endpoints respond
log "Test 2: Enable all metrics"
apply_metrics_config "all" ""

log "Waiting for API metrics endpoint ($METRICS_API_URL)"
wait_for_metrics "$METRICS_API_URL" "API"
log "API metrics endpoint responding - OK"

log "Waiting for Microservices metrics endpoint ($METRICS_MICROSERVICES_URL)"
wait_for_metrics "$METRICS_MICROSERVICES_URL" "Microservices"
log "Microservices metrics endpoint responding - OK"

# Test 3: Validate Prometheus format
log "Test 3: Validate Prometheus metrics format"

api_body=$(curl -fsS "$METRICS_API_URL")
if ! grep -q "^# HELP" <<< "$api_body"; then
    die "API metrics missing HELP lines - not valid Prometheus format"
fi

if ! grep -q "^# TYPE" <<< "$api_body"; then
    die "API metrics missing TYPE lines - not valid Prometheus format"
fi

metric_names_to_file "$api_body" "$ALL_API_METRIC_NAMES"

log "API metrics valid Prometheus format - OK"

ms_body=$(curl -fsS "$METRICS_MICROSERVICES_URL")
if ! grep -q "^# HELP" <<< "$ms_body"; then
    die "Microservices metrics missing HELP lines - not valid Prometheus format"
fi

if ! grep -q "^# TYPE" <<< "$ms_body"; then
    die "Microservices metrics missing TYPE lines - not valid Prometheus format"
fi

log "Microservices metrics valid Prometheus format - OK"

# Test 4: Verify expected metric names exist
log "Test 4: Check for expected Immich metrics"

if ! grep -q "process_cpu" <<< "$api_body"; then
    die "API metrics missing process_cpu metrics (host metrics)"
fi
log "Host metrics present - OK"

# Test 5: Enable only specific metrics category
log "Test 5: Test selective metrics (api only)"
apply_metrics_config "api" ""

wait_for_metrics "$METRICS_API_URL" "API"
api_only_body=$(curl -fsS "$METRICS_API_URL")
if ! grep -q "^# HELP" <<< "$api_only_body"; then
    die "API-only metrics missing HELP lines - not valid Prometheus format"
fi

if ! grep -q "^# TYPE" <<< "$api_only_body"; then
    die "API-only metrics missing TYPE lines - not valid Prometheus format"
fi

metric_names_to_file "$api_only_body" "$API_ONLY_METRIC_NAMES"

if cmp -s "$ALL_API_METRIC_NAMES" "$API_ONLY_METRIC_NAMES"; then
    die "API-only metrics exported the same metric families as include=all"
fi

if comm -23 "$API_ONLY_METRIC_NAMES" "$ALL_API_METRIC_NAMES" | grep -q .; then
    die "API-only metrics exported families that were not present in include=all"
fi

if ! comm -23 "$ALL_API_METRIC_NAMES" "$API_ONLY_METRIC_NAMES" | grep -q .; then
    die "API-only metrics did not remove any metric families from include=all"
fi

if grep -q "process_cpu" "$API_ONLY_METRIC_NAMES"; then
    die "API-only metrics still include host process_cpu metrics"
fi

log "Selective API metrics changed the metric family set - OK"

# Test 6: Test include/exclude combination
log "Test 6: Test include all / exclude api"
apply_metrics_config "all" "api"

wait_for_metrics "$METRICS_API_URL" "API"
all_except_api_body=$(curl -fsS "$METRICS_API_URL")
if ! grep -q "^# HELP" <<< "$all_except_api_body"; then
    die "Exclude=api metrics missing HELP lines - not valid Prometheus format"
fi

if ! grep -q "^# TYPE" <<< "$all_except_api_body"; then
    die "Exclude=api metrics missing TYPE lines - not valid Prometheus format"
fi

metric_names_to_file "$all_except_api_body" "$ALL_EXCEPT_API_METRIC_NAMES"

if cmp -s "$ALL_API_METRIC_NAMES" "$ALL_EXCEPT_API_METRIC_NAMES"; then
    die "Exclude=api exported the same metric families as include=all"
fi

if comm -23 "$ALL_EXCEPT_API_METRIC_NAMES" "$ALL_API_METRIC_NAMES" | grep -q .; then
    die "Exclude=api exported families that were not present in include=all"
fi

if ! comm -23 "$ALL_API_METRIC_NAMES" "$ALL_EXCEPT_API_METRIC_NAMES" | grep -q .; then
    die "Exclude=api did not remove any metric families from include=all"
fi

if ! comm -23 "$API_ONLY_METRIC_NAMES" "$ALL_EXCEPT_API_METRIC_NAMES" | grep -q .; then
    die "Exclude=api did not remove any metric families that were present in API-only mode"
fi

if ! grep -q "process_cpu" "$ALL_EXCEPT_API_METRIC_NAMES"; then
    die "Exclude=api unexpectedly removed host process_cpu metrics"
fi

log "Include/exclude combination changed the metric family set - OK"

# Test 7: Disable metrics again
log "Test 7: Disable metrics"
apply_metrics_config "" ""

api_status=$(http_code "$METRICS_API_URL")
if [ "$api_status" = "200" ]; then
    die "API metrics endpoint returned 200 after disabling metrics"
fi

microservices_status=$(http_code "$METRICS_MICROSERVICES_URL")
if [ "$microservices_status" = "200" ]; then
    die "Microservices metrics endpoint returned 200 after disabling metrics"
fi

log "Metrics disabled again - OK"

rm -rf "$TMPDIR_METRICS"

log "All metrics tests completed successfully ✅"
