+++
template = "blog-post.html"
title = "VectorChord Migration Finalized"
date = "2026-07-05"
path = "news/2026/07/05/vectorchord-migration-finalized"
authors = ["nsg"]
+++

The [VectorChord migration](/news/2025/08/31/vectorchord-migration-rollout/) that rolled out last year is now complete. The next release performs the final cleanup step: dropping the empty `vectors` schema that pgvecto.rs left behind ([#327](https://github.com/nsg/immich-distribution/issues/327)).

The pgvecto.rs extension itself is already gone. Immich dropped it from the database automatically after the migration, and the package stopped shipping it with era 2 (v2.5.6). The only trace left on systems that lived through the migration is an empty `vectors` schema in the database.

Starting with the next release, this schema is removed automatically when the database service starts. The cleanup is safe: it only removes the schema if it exists, and it refuses to touch a schema that unexpectedly contains data. Fresh installs never had the schema and are unaffected. No action is needed on your part.
