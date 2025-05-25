---
title: "Stuck at v1.133.1"
date: 2025-05-25
authors: [nsg]
---

If you found yourself stuck at version 1.133.1 with this error message, continue reading.

```
error: cannot perform the following tasks:
- Run pre-refresh hook of "immich-distribution" snap if present (run hook "pre-refresh": 
-----
/snap/immich-distribution/195/snap/hooks/pre-refresh: line 9: /snap/immich-distribution/195/backup: No such file or directory
Failed to create and validate database backup during pre-refresh.
-----)
```

1. Disable the hook by executing `touch /var/snap/immich-distribution/common/no-pre-refresh-hook`
2. Update as you normally do (for example, `snap refresh`).
3. Restore the hook by executing `rm /var/snap/immich-distribution/common/no-pre-refresh-hook`

Only people running the unstable edge, beta, and candidate channels need to do this. This bug was caught in testing before it hit the stable channel.
