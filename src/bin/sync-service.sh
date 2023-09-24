#!/bin/bash

. $SNAP/bin/load-env

export PGDATA="$SNAP_COMMON/pgsql/data"
export PYTHONPATH="$SNAP/opt/pipsyncenv"

while ! sync_enabled; do
    sleep 3600
done

while ! immich_server_ready; do
    echo "Immich server not ready yet, waiting ..."
    sleep 10
done

while ! $SNAP/usr/local/pgsql/bin/pg_isready 2>&1 > /dev/null; do
    echo "Postgres not ready yet, waiting ..."
    sleep 2
done

cat $SNAP/etc/modify-db.sql | $SNAP/bin/psql -d immich

SYNC_FILE_AGE_DELETE_LIMIT="$(snapctl get sync-file-age-delete-limit)"
if [ -z "$SYNC_FILE_AGE_DELETE_LIMIT" ]; then
    # Default to 100 years, this more or less disables the feature
    # This user need to explicitly set this to a lower value to enable it
    SYNC_FILE_AGE_DELETE_LIMIT=36500
fi

for KEY in $(snapctl get sync); do
    {
        IMMICH_API_KEY="$KEY" SYNC_FILE_AGE_DELETE_LIMIT="$SYNC_FILE_AGE_DELETE_LIMIT" $SNAP/usr/local/bin/python3 $SNAP/bin/sync-service.py
    } &
done

wait
