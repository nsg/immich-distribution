#!/bin/bash

. $SNAP/bin/load-env

export PGDATA="$SNAP_COMMON/pgsql/data"
export PYTHONPATH="$SNAP/sync/lib/python3.11/site-packages/"

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

for KEY in $(snapctl get sync); do
    {
        IMMICH_API_KEY="$KEY" $SNAP/sync/bin/sync-service
    } &
done

wait
