#!/bin/bash

log() {
    echo -e "🔧 CLI TEST: $@"
}

die() {
    echo "💥 CLI TEST FAILED: $@" >&2
    exit 1
}

get_ip_address() {
    ip route get 8.8.8.8 | grep -oP 'src \K[^ ]+'
}

log "Starting CLI API key tests"

log "Generating new API key using immich-admin CLI"

api_key=$(sudo immich-distribution.immich-admin create-api-key test-cli-key 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$api_key" ]; then
    die "API key generation failed - CLI command returned error or empty result"
fi

log "API key generated: ${api_key:0:10}... (length: ${#api_key} chars)"

log "Testing API key with users endpoint"

ip=$(get_ip_address)
log "Server IP: $ip"

response=$(curl -s "http://${ip}/api/users" \
    -H "Accept: application/json" \
    -H "X-API-KEY: $api_key" \
    -w "%{http_code}")

http_code="${response: -3}"
body="${response%???}"

log "API response: HTTP $http_code"

if [ "$http_code" != "200" ]; then
    die "API request failed with HTTP $http_code - Response: $body"
fi

if ! echo "$body" | jq -e '.[0].id' > /dev/null 2>&1; then
    die "Invalid API response format - Expected user array with id field"
fi

user_count=$(echo "$body" | jq '. | length')
log "Successfully retrieved $user_count users via API"

log "CLI tests completed successfully ✅"
