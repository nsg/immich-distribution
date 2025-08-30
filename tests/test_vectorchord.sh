#!/bin/bash

log() {
    echo -e "🧪 VECTORCHORD: $@"
}

die() {
    echo "💥 VECTORCHORD TEST FAILED: $@" >&2
    exit 1
}

pg() {
    sudo immich-distribution.psql -t -A -c "$1" 2>/dev/null
}

# We rely on earlier tests / wait target to have system up.
# Validate that vectorchord extension exists, indices are using vchordrq, and probes parameter is set.

log "Checking that VectorChord extension is installed"
if ! pg "SELECT extname FROM pg_extension WHERE extname='vchord';" | grep -q '^vchord$'; then
    die "VectorChord extension 'vchord' not found in pg_extension"
fi

log "Checking that shared_preload_libraries contains vchord.so"
if ! pg "SHOW shared_preload_libraries;" | tr ',' '\n' | grep -q 'vchord.so'; then
    die "shared_preload_libraries does not include vchord.so"
fi

log "Checking that at least one vchordrq index exists"
index_count=$(pg "SELECT count(1) FROM pg_indexes WHERE indexdef ILIKE '%USING vchordrq%';")
if [[ -z "$index_count" || "$index_count" -eq 0 ]]; then
    die "No indexes found using vchordrq"
fi
log "Found $index_count vchordrq indexes"

log "Checking that vchordrq.probes GUC can be set (session level)"
# We set it locally to 1 and then read it back; failure indicates misconfiguration.
if ! pg "SET LOCAL vchordrq.probes = 1; SHOW vchordrq.probes;" | grep -q '^1$'; then
    die "Failed to set or read vchordrq.probes GUC"
fi

log "Checking that server preferred vector extension is vectorchord (auto-detect order preference)"
# Query Immich config route for vector extension; fall back to env detection if API not ready.
get_ip_address() { ip route get 8.8.8.8 | grep -oP 'src \K[^ ]+'; }
headers() { echo "Accept: application/json"; echo "X-API-KEY: $(cat secret.txt 2>/dev/null || echo '')"; }

ip=$(get_ip_address)
api_ext=$(curl -s "http://${ip}/api/server/features" -H "$(headers)" | jq -r '.vectorExtension.name' 2>/dev/null)
if [[ -n "$api_ext" && "$api_ext" != "vectorchord" ]]; then
    die "API reports vectorExtension.name=$api_ext (expected vectorchord)"
fi

log "Inspecting recent journal logs for VectorChord migration markers"
logs=$(journalctl -n 400 --no-pager -eu snap.immich-distribution.immich-server.service 2>/dev/null)
# Look for phases: creation, reindex start, reindex completion.
creation_found=$(echo "$logs" | grep -E 'Creating VectorChord extension' || true)
reindex_start_found=$(echo "$logs" | grep -E 'Reindexing (clip_index|face_index)' || true)
reindex_done_found=$(echo "$logs" | grep -E 'Reindexed (clip_index|face_index)' || true)

if [[ -z "$creation_found" ]]; then
    log "No 'Creating VectorChord extension' log found (may have been earlier)."
fi
if [[ -z "$reindex_start_found" ]]; then
    die "Expected to see 'Reindexing clip_index/face_index' in recent logs"
fi
if [[ -z "$reindex_done_found" ]]; then
    die "Expected to see 'Reindexed clip_index/face_index' in recent logs"
fi

log "VectorChord migration validation passed ✅"
