---
title: "Stuck at v1.133.1"
date: 2025-05-25
authors: [nsg]
---

If you find yourself stuck at version 1.133.1 with one of the following error messages, please continue reading.

```
error: cannot perform the following tasks:
- Run pre-refresh hook of "immich-distribution" snap if present (run hook "pre-refresh": 
-----
/snap/immich-distribution/195/snap/hooks/pre-refresh: line 9: /snap/immich-distribution/195/backup: No such file or directory
Failed to create and validate database backup during pre-refresh.
-----)
```

```
error: cannot perform the following tasks:
- Run pre-refresh hook of "immich-distribution" snap if present (run hook "pre-refresh": 
-----
Creating database backup: /var/snap/immich-distribution/common/backups/immich_database_v1.133.1_pgvectors.sql.xz

<exceeded maximum runtime of 10m0s>
-----)
```

To resolve this, follow these steps:

1. Disable the hook by executing: `touch /var/snap/immich-distribution/common/no-pre-refresh-hook`
2. Update as you normally would (for example, `snap refresh`).
3. Restore the hook by executing: `rm /var/snap/immich-distribution/common/no-pre-refresh-hook`

Only users on the unstable `edge`, `beta`, or `candidate` channels need to perform these steps. This bug was identified during testing before it affected the `stable` channel.

### Technical background

In preparation for the upcoming migration from pgvecto.rs to VectorChord, a database backup step was added to the `pre-refresh` hook. This hook is designed to back up the database before a snap update occurs. However, a bug was introduced in the `pre-refresh` script in revision `195` due to an incorrect path being committed.

Although a fix was implemented in the subsequent revision, users who had already updated to revision `195` found themselves stuck. This was because the `pre-refresh` hook runs *before* the update process, causing the update to fail repeatedly due to the faulty script.

Unfortunately, there was no way to automatically push a fix for this issue to affected users. Thankfully, a mechanism to disable the hook was already in place, which is the solution employed here.

Later, during further testing, it was discovered that on some systems, the database backup process could exceed the 10-minute timeout. This scenario would trigger a similar problem, effectively blocking the update.

Given these challenges, the decision has been made to revert this pre-refresh backup feature for now.
