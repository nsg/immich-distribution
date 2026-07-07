+++
template = "blog-post.html"
title = "Legacy Sync Service Removed"
date = "2026-07-06"
path = "news/2026/07/06/sync-service-removed"
authors = ["nsg"]
+++

The built-in Python sync service has been removed with the Immich v3 upgrade. It was [already deprecated](/news/2026/03/13/immich-sync/) in favor of [Immich Sync Service](https://github.com/nsg/immich-sync), a standalone Rust rewrite that talks to the Immich API instead of the database and works with any Immich deployment.

On upgrade, the snap cleans up after the old service automatically: the custom database tables and trigger it created (`assets_delete_audits`, `assets_filesync_lookup`, and the delete trigger on the `asset` table) are dropped, and the old `sync-enabled` and `sync-delete-threshold` snap configuration options are removed. Your synced photos are not touched.

If you were using the old sync feature, migrate to [immich-sync](https://github.com/nsg/immich-sync). It covers everything the built-in service did, with more control over deletion policies, and it can run on any machine that can reach your Immich server.
