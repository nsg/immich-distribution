+++
title = "Migrate from Docker"
+++

# Migrate from Docker

This guide walks you through migrating from the official Docker Compose deployment to Immich Distribution (the snap package). Immich has a built-in backup and restore system accessible from the web UI. The database backups it produces (`.sql.gz` files) work the same way regardless of whether Immich is running in Docker or as a snap.

## 1. Create a backup

Create a database backup from the Immich web UI. See the [official Immich backup documentation](https://immich.app/docs/administration/backup-and-restore) for details.

## 2. Install Immich Distribution

Follow the [installation guide](/installation/) to install the snap.

## 3. Move your assets

Copy your photos and videos from Docker's `UPLOAD_LOCATION` (defined in your `.env` file) to the snap's upload directory at `/var/snap/immich-distribution/common/upload/`.

## 4. Restore the database backup

Open the Immich web UI and click **Restore from backup** on the onboarding screen. Upload your `.sql.gz` backup file and wait for the restore to complete. See the [official Immich restore documentation](https://immich.app/docs/administration/backup-and-restore) for details.

## 5. Verify

Log in and check that your photos, albums, and metadata are present. Thumbnails and encoded videos will be regenerated automatically if missing. Face recognition and smart search may need time to reprocess.

{% admonition(type="info", title="Tested in CI") %}
This migration path is automatically tested in CI. On every build, a fresh Docker Immich instance is populated with test data, a built-in backup is taken, and then restored into the snap through the official onboarding restore flow. The test verifies user authentication, asset metadata, file integrity (SHA-256), and smart search.
{% end %}
