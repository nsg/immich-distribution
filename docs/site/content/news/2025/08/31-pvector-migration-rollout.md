+++
template = "blog-post.html"
title = "VectorChord Migration Rollout"
date = "2025-08-31"
path = "news/2025/08/31/vectorchord-migration-rollout"
authors = ["nsg"]
+++


The VectorChord migration from pgvecto.rs to VectorChord, which was [announced earlier this month](/news/2025/08/01/important-notifications--backup-database/), has started rolling out today from revision 228 and forward.

This automatic migration will move your Immich instance from the deprecated pgvecto.rs extension to its replacement VectorChord.

## Future Cleanup Plan

The migration follows a phased approach to ensure stability:

- **Revision 228+**: VectorChord migration begins rolling out
- **Revision 236+**: Remove pgvecto.rs from the image ([#326](https://github.com/nsg/immich-distribution/issues/326))
- **Revision 245+**: Clean up old pgvecto.rs database schema ([#327](https://github.com/nsg/immich-distribution/issues/327))

For more details about this migration, see the [earlier announcement](/news/2025/08/01/important-notifications--backup-database/).

