+++
title = "Migrate from Immich Docker to Immich Distribution (snap)"
draft = true
+++

# Migrate from Immich Docker to Immich Distribution (snap)

This guide walks you through migrating an existing Immich deployment that uses Docker Compose to Immich Distribution.

{% admonition(type="warning", title="Important") %}
The Immich version must match between your Docker deployment and the snap you install. Do not attempt to migrate across versions, and if you must, migrate from an older version to a newer.
{% end %}

## 1. Backup Database

Make a complete backup of your current Immich installation. You need these backups to restore your installation to Immich Distribution. A backup is also handy if the migration fails and you need to go back to Docker Compose.

Read and follow the [official Immich docs for backups](https://immich.app/docs/administration/backup-and-restore), but as of september 2025, trigger the backups with the following commands:

```
# Load DB_USERNAME from .env
export $(grep DB_USERNAME .env)

# Dump (backup) the database
docker exec -t immich_postgres pg_dumpall --clean --if-exists --username=$DB_USERNAME | xz > backup.sql.xz
```

Please note that I compress the database with `xz` and not `gzip`, I do this to make the backup compatible with the build in restore command in Immich Distribution.

## 2. Stop Docker Compose

Show down the old Docker Compose based installation

```
docker compose down
```

## 3. Install Immich Distribution

```
sudo snap install immich-distribution
```

## 4. Move library to the snap

Move the files in `UPLOAD_LOCATION` (from .env) to `/var/snap/immich-distribution/common/upload`. For example if the default option of `UPLOAD_LOCATION=./library` is defined execute this:

```
sudo rsync -r ./library/* /var/snap/immich-distribution/common/upload
```

## 5. Restore database

```
sudo mv backup.sql.xz /var/snap/immich-distribution/common/backups/
sudo immich-distribution.restore -y -d /var/snap/immich-distribution/common/backups/backup.sql.xz
```

## Align versions (must match)

Check which Immich version your Docker deployment ran and install the matching snap revision/channel.

- List available versions/channels in our docs Install page (the table is embedded from the Snap Store)
- Optionally pin a specific revision:

```bash
sudo snap refresh immich-distribution --revision <REVISION>
```

Do not proceed until the versions match. Migrating across versions can fail due to schema differences.

## Move your data into the snap

There are two paths: use the snap’s built‑in restore for database and copy assets manually (recommended), or use the bundled asset restore if you created an assets tarball with the snap’s backup tool. Most Docker users will copy assets manually.

### 1) Restore the database into the snap

First, convert your `dump.sql.gz` (gzip) to the `.sql.xz` format expected by the restore helper, or import directly by piping. Two options are shown below.

Option A — convert to xz file:

```bash
# Place backups under the snap backup folder
sudo mkdir -p /var/snap/immich-distribution/common/backups
sudo cp /path/to/backup/dump.sql.gz /var/snap/immich-distribution/common/backups/
cd /var/snap/immich-distribution/common/backups

# Convert to xz
sudo gunzip -c dump.sql.gz | xz > dump.sql.xz

# Restore using the helper (will stop services, reset DB, import, then restart)
sudo immich-distribution.restore -y -d /var/snap/immich-distribution/common/backups/dump.sql.xz
```

Option B — pipe directly without creating an xz file:

```bash
# Stop services and prepare database
sudo snap stop immich-distribution
sudo snap stop immich-distribution.postgres || true
sudo rm -rf /var/snap/immich-distribution/common/pgsql/data
sudo snap start immich-distribution.postgres

# Wait a few seconds for Postgres to be ready, then import
sudo bash -lc 'while ! /snap/immich-distribution/current/usr/local/pgsql/bin/pg_isready; do sleep 1; done'

# Import with the same sed adjustments the helper uses
sudo bash -lc 'gunzip -c /path/to/backup/dump.sql.gz \
  | sed "s/SELECT pg_catalog.set_config(\'search_path\', \'\', false);/SELECT pg_catalog.set_config(\'search_path\', \'public, pg_catalog\', true);/g" \
  | sed "/^DROP ROLE/d" | sed "/^CREATE ROLE/d" | sed "/^ALTER ROLE/d" \
  | /snap/immich-distribution/current/usr/local/pgsql/bin/psql -U postgres -v ON_ERROR_STOP=1'

# Restart Immich services
sudo snap start immich-distribution
```

 The helper `immich-distribution.restore -d` does all the DB service handling and applies the necessary sed adjustments automatically when given an `.sql.xz` dump.

### 2) Copy asset files

 Copy your Immich files from Docker’s `UPLOAD_LOCATION` into the snap’s upload directory. The snap expects assets under:

- `/var/snap/immich-distribution/common/upload/`
  - `upload/` — original assets per user
  - `profile/` — user avatars
  - `library/` — optional, only if you used the storage template engine

Example:

```bash
sudo rsync -aH --info=progress2 /path/to/UPLOAD_LOCATION/upload/ /var/snap/immich-distribution/common/upload/upload/
sudo rsync -aH --info=progress2 /path/to/UPLOAD_LOCATION/profile/ /var/snap/immich-distribution/common/upload/profile/
# Only if you used storage templates
[ -d /path/to/UPLOAD_LOCATION/library ] && sudo rsync -aH --info=progress2 /path/to/UPLOAD_LOCATION/library/ /var/snap/immich-distribution/common/upload/library/
```

Keep the directory structure intact. Do not manually alter contents of thumbs/ or encoded-video/—they will be regenerated if missing.

## Start and verify

Start services if they aren’t running already:

```bash
sudo snap start immich-distribution
```

Open the Immich web app and verify that:
- Users can sign in
- Albums and metadata are present
- A few photos/videos open correctly

 If you backed up only `upload/` and `profile/`, Immich will regenerate thumbnails and encoded videos over time.

## Post‑migration

- Configure HTTPS and security options as needed (see [Configuration](/configuration/))
- Consider enabling the daily database backup service:

```bash
sudo snap set immich-distribution backup-database-daily=true
```

- Once satisfied, remove or archive your Docker compose deployment

## Troubleshooting

- Version mismatch: ensure the snap version matches your old Docker version before restoring
- Restore errors about existing relations/constraints: ensure the DB was reset (the helper does this), and that services didn’t run migrations during import
- Missing files: confirm you copied the proper `upload/`, `profile/`, and (if used) `library/` trees
- Out‑of‑sync backup: if assets and DB are slightly out of sync, some items may be missing or orphaned; re‑upload missing files if needed
