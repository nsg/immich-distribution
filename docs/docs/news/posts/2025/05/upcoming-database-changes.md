---
title: "Upcoming database changes"
date: 2025-05-22
authors: [nsg]
---

# Upcoming database changes

Immich version 1.133.0 replaces the deprecated [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) extension with its replacement [VectorChord](https://github.com/tensorchord/VectorChord). To ease transition, Immich will support both in parallel for a few releases.

There is also a breaking change in the API between the mobile application and the server. With this in mind, I will fast-track this release and postpone the VectorChord change to a later, separate release.

!!! Danger "Breaking change in the mobile app"
    Please ensure both your mobile app and the server are updated to v1.133.0.
    Older versions of the Immich mobile app will **not** work correctly with server version v1.133.0.

## Upgrading from 1.107.2 or older

Due to the automatic updates in the package format, most users are on recent versions. Snap Store metrics show that only 0.5% of users are running releases this old. If you are one of these rare users, you need to manually update to a newer intermediate release before upgrading to the most recent release.

## Automatic database backup

An upcoming update will include a feature that performs a one-time automatic backup of your database. This backup is a precautionary measure, aligning with upstream recommendations, to safeguard your data during the transition and provide a recovery point should any issues arise.

The backup file will be saved to `/var/snap/immich-distribution/common/backups/immich_database_*_pgvectors.sql.xz`.

Please be aware that this backup process will consume additional disk space. If your installation has limited storage, there is a small risk of running out of disk space. This backup will be automatically removed in a future update to reclaim disk space for users who no longer require it.

If you require assistance or encounter any issues, please open an issue in the GitHub repository.
