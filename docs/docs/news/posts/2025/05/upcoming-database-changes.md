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
    Older versions of the Immich mobile app will **not** work correctly with server version v1.133.0. The updated mobile app should be available on the respective app stores concurrently with this server release.

## Upgrading from 1.107.2 or older

Due to the automatic updates in the package format, most users are on recent versions. Snap Store metrics show that only 0.5% of users are running releases this old. To protect these users, I will block updates from versions older than 1.107.2 in the release containing the VectorChord migration. If you are one of these rare users, you need to manually update to a newer intermediate release.
