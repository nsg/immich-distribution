+++
title = "Migrate to Docker"
+++

# Migrate to Docker

This guide walks you through migrating from Immich Distribution (the snap package) to the official Docker Compose deployment. Immich has a built-in backup and restore system accessible from the web UI. The database backups it produces (`.sql.gz` files) work the same way regardless of whether Immich is running as a snap or in Docker.

{% admonition(type="warning", title="Use Immich's built-in backup, not the snap CLI") %}
The snap also has its own CLI backup tool (`immich-distribution.backup`) that produces `.sql.xz` files in a different format. Do not use the snap CLI backup for this migration — use Immich's built-in backup from the web UI instead.
{% end %}

## 1. Create a backup

Create a database backup from the Immich web UI. See the [official Immich backup documentation](https://immich.app/docs/administration/backup-and-restore) for details. The backup file will be stored at `/var/snap/immich-distribution/common/upload/backups/`.

## 2. Move your assets

Copy your photos and videos from the snap's upload directory to a location that Docker can access. This will become your `UPLOAD_LOCATION` in the Docker `.env` file.

## 3. Do a fresh install

Follow the [official Immich Docker installation guide](https://immich.app/docs/install/docker-compose). Set `UPLOAD_LOCATION` in the `.env` file to point to your copied assets.

## 4. Restore the database backup

Open the Immich web UI and click **Restore from backup** on the onboarding screen. Upload your `.sql.gz` backup file and wait for the restore to complete. See the [official Immich restore documentation](https://immich.app/docs/administration/backup-and-restore) for details.

## 5. Verify

Log in and check that your photos, albums, and metadata are present. Thumbnails and encoded videos will be regenerated automatically if missing. Face recognition and smart search may need time to reprocess.

{% admonition(type="info", title="Tested in CI") %}
This migration path is automatically tested in CI. On every build, a built-in Immich backup from the snap is restored into a fresh upstream Docker Immich stack through the official onboarding restore flow. The test verifies user authentication, asset metadata, file integrity (SHA-256), and smart search.
{% end %}
