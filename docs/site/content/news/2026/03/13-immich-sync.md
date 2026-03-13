+++
template = "blog-post.html"
title = "Introducing Immich Sync Service"
date = "2026-03-13"
path = "news/2026/03/13/immich-sync"
authors = ["nsg"]
+++

The sync feature in Immich Distribution is being replaced. [Immich Sync Service](https://github.com/nsg/immich-sync) is a ground-up rewrite in Rust that replaces the built-in Python sync component with something faster, more portable, and easier to maintain.

## Why a rewrite?

The original sync service was written in Python and tightly coupled to this Snap package. It connected directly to Immich's PostgreSQL database using custom tables and a deletion trigger to detect when assets were removed. That worked, but it had real downsides:

- **Database coupling**: Custom tables (`assets_delete_audits`, `assets_filesync_lookup`) and a trigger on Immich's `asset` table risked conflicts with upstream schema migrations.
- **Tied to immich-distribution**: Direct database access meant it could theoretically work with other Immich installations, but that would require additional setup and configuration work.

The Immich API has matured significantly since the original was written. Endpoints now exist for everything the sync service needs, so direct database access is no longer necessary.

## What changed

The new service is written in Rust and talks exclusively to the Immich API. It uses a local SQLite database for bookkeeping instead of injecting tables into Immich's PostgreSQL. This means it works with **any** Immich deployment, not just immich-distribution.

The architecture is similar: four workers per user handle file watching, periodic full scans, upload queuing, and deletion reconciliation. But the implementation is cleaner:

- **No database triggers** -- deletion detection uses the Immich API.
- **Local SQLite** -- all state is in a single file, easy to inspect or reset.
- **Configurable policies** -- `delete_threshold` and `delete_max_age` give you fine-grained control over when local deletes propagate to Immich.
- **Cross-platform** -- pre-built binaries are available for Linux (x86_64, aarch64), macOS, and Windows.
- **Event logging** -- optional JSONL event log for auditing uploads, deletes, and skipped actions.

One of the nice things about this approach is that the sync service can run anywhere -- it does not need to be on the same machine as Immich. As long as it can reach the Immich API, it works. You could run it on your desktop, a NAS, or wherever your sync folder lives.

## What this means for immich-distribution

I have just moved over to the new sync service myself. Once I consider it stable enough, I plan to formally deprecate the built-in Python sync service in immich-distribution in favor of the standalone project.

The project is still early -- currently at v0.1.x -- so expect rough edges and breaking changes. I will release it as 1.0 before formally deprecating the built-in Python sync service. Until then, the built-in sync will continue to work, but new development will happen in the [immich-sync](https://github.com/nsg/immich-sync) repository. If you are currently using the sync feature, I encourage you to try the new service and [report any issues](https://github.com/nsg/immich-sync/issues).

