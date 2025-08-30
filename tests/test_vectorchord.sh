#!/bin/bash

log() {
    echo -e "🧪 $@"
}

error() {
    echo "❌ $@" >&2
    ((failures++))
}

success() {
    echo "✅ $@"
}

pg() {
    sudo immich-distribution.psql -d immich -tA <<< "$1"
}

failures=0

log "Listing all installed extensions"
pg "SELECT extname FROM pg_extension;"

log "Checking that VectorChord extension is installed"
if ! pg "SELECT extname FROM pg_extension WHERE extname='vchord';" | grep -q '^vchord$'; then
    error "VectorChord extension 'vchord' not found in pg_extension"
else
    success "VectorChord extension is installed"
fi

log "Checking that pgvecto.rs extension has been dropped"
if pg "SELECT extname FROM pg_extension WHERE extname='vectors';" | grep -q '^vectors$'; then
    error "pgvecto.rs extension 'vectors' should have been dropped but still exists"
else
    success "pgvecto.rs extension has been dropped"
fi

log "Checking that pgvector extension is still loaded (dependency for VectorChord)"
if ! pg "SELECT extname FROM pg_extension WHERE extname='vector';" | grep -q '^vector$'; then
    error "pgvector extension 'vector' should still be loaded as VectorChord dependency"
else
    success "pgvector extension is still loaded as dependency"
fi

log "Checking that vectors schema still exists (manual drop required)"
if ! pg "SELECT schema_name FROM information_schema.schemata WHERE schema_name='vectors';" | grep -q '^vectors$'; then
    log "Note: vectors schema not found (may have been manually dropped already)"
else
    success "vectors schema still exists (requires manual DROP SCHEMA vectors)"
fi

log "Inspecting recent journal logs for VectorChord migration markers"
logs=$(journalctl -n 400 --no-pager -eu snap.immich-distribution.immich-server.service 2>/dev/null)

if [[ -z "$(echo "$logs" | grep -E 'Creating VectorChord extension' || true)" ]]; then
    log "No 'Creating VectorChord extension' log found (may have been earlier)."
fi

if [[ -z "$(echo "$logs" | grep -E 'Reindexing clip_index' || true)" ]]; then
    error "Expected to see 'Reindexing clip_index' in recent logs"
else
    success "Found 'Reindexing clip_index' in recent logs"
fi

if [[ -z "$(echo "$logs" | grep -E 'Reindexed clip_index' || true)" ]]; then
    error "Expected to see 'Reindexed clip_index' in recent logs"
else
    success "Found 'Reindexed clip_index' in recent logs"
fi

if [[ -z "$(echo "$logs" | grep -E 'Reindexing face_index' || true)" ]]; then
    error "Expected to see 'Reindexing face_index' in recent logs"
else
    success "Found 'Reindexing face_index' in recent logs"
fi

if [[ -z "$(echo "$logs" | grep -E 'Reindexed face_index' || true)" ]]; then
    error "Expected to see 'Reindexed face_index' in recent logs"
else
    success "Found 'Reindexed face_index' in recent logs"
fi

if [[ $failures -gt 0 ]]; then
    echo "💥 VECTORCHORD TEST FAILED: $failures error(s) found" >&2
    exit 1
fi

log "VectorChord migration validation passed ✅"
