---
date: 2025-08-31
authors: [nsg]
categories:
  - Database
  - Migrations
---

# VectorChord Migration Rollout

The VectorChord migration from pgvecto.rs to VectorChord, which was [announced earlier this month](01-notifications-announcement.md), has started rolling out today from revision 228 and forward.

This automatic migration will move your Immich instance from the deprecated pgvecto.rs extension to its replacement VectorChord.

## Future Cleanup Plan

The migration follows a phased approach to ensure stability:

- **Revision 228+**: VectorChord migration begins rolling out
- **Revision 236+**: Remove pgvecto.rs from the image ([#326](https://github.com/nsg/immich-distribution/issues/326))
- **Revision 245+**: Clean up old pgvecto.rs database schema ([#327](https://github.com/nsg/immich-distribution/issues/327))

For more details about this migration, see the [earlier announcement](01-notifications-announcement.md).

