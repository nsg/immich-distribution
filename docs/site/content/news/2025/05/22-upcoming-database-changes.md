+++
template = "blog-post.html"
title = "Upcoming database changes"
date = "2025-05-22"
path = "news/2025/05/22/upcoming-database-changes"
authors = ["nsg"]
+++


Immich version 1.133.0 replaces the deprecated [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) extension with its replacement [VectorChord](https://github.com/tensorchord/VectorChord). To ease transition, Immich will support both in parallel for a few releases.

There is also a breaking change in the API between the mobile application and the server. With this in mind, I will fast-track this release and postpone the VectorChord change to a later, separate release.

{% admonition(type="danger", title="Breaking change in the mobile app") %}
Please ensure both your mobile app and the server are updated to v1.133.0.
Older versions of the Immich mobile app will **not** work correctly with server version v1.133.0.
{% end %}

## Upgrading from 1.107.2 or older

Due to the automatic updates in the package format, most users are on recent versions. Snap Store metrics show that only 0.5% of users are running releases this old. If you are one of these rare users, you need to manually update to a newer intermediate release before upgrading to the most recent release.

## Database backup

There are a lot of database changes, which introduces some risk. If you have not done so already, this is probably a good time to enable automatic database backups. You can either use the [built in backup job](https://immich.app/docs/administration/backup-and-restore#automatic-database-dumps) (should be enabled by default), or the [backup tool included in this snap](/configuration/backup-restore/).

Use `immich-distribution.backup -l` to list existing backups.
