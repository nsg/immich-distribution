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

log "Verifying pre-upgrade state (pgvecto.rs should be active)"

log "Listing all installed extensions"
pg "SELECT extname FROM pg_extension;"
log "✅ Extensions listed successfully"

log "Checking that pgvecto.rs extension is installed"
if ! pg "SELECT extname FROM pg_extension WHERE extname='vectors';" | grep -q '^vectors$'; then
    error "pgvecto.rs extension 'vectors' not found in pg_extension"
else
    success "pgvecto.rs extension is installed"
fi

log "Checking that VectorChord extension is NOT installed"
if pg "SELECT extname FROM pg_extension WHERE extname='vchord';" | grep -q '^vchord$'; then
    error "VectorChord extension 'vchord' should not be installed before upgrade"
else
    success "VectorChord extension is not installed (as expected)"
fi

log "Checking that pgvector extension is NOT installed"
if pg "SELECT extname FROM pg_extension WHERE extname='vector';" | grep -q '^vector$'; then
    error "pgvector extension 'vector' should not be installed before upgrade"
else
    success "pgvector extension is not installed (as expected)"
fi

log "Checking that vectors schema exists (pgvecto.rs workspace)"
if ! pg "SELECT schema_name FROM information_schema.schemata WHERE schema_name='vectors';" | grep -q '^vectors$'; then
    error "vectors schema should exist before upgrade"
else
    success "vectors schema exists"
fi

if [[ $failures -gt 0 ]]; then
    echo "💥 VECTORCHORD PRE-UPGRADE TEST FAILED: $failures error(s) found" >&2
    exit 1
fi

log "Pre-upgrade state validation passed ✅"
