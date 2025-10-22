+++
template = "blog-post.html"
title = "Breaking Change in v1.137: Upgrade Required for Older Versions"
date = "2025-08-03"
path = "news/2025/08/03/breaking-change-in-v1137-upgrade-required-for-older-versions"
authors = ["nsg"]
+++


Immich v1.137.0 introduces a breaking change affecting users on versions older than v1.132.0 (released May 9, 2025). If you have automatic updates enabled (default), no action is required. However, the few users running older versions must manually upgrade to an intermediate version first.

## Required Action

If running a version older than v1.132.0:

1. Upgrade to v1.136.0 first:
   ```bash
   sudo snap refresh immich-distribution --revision=218
   ```
2. Allow Immich to start successfully
3. Then upgrade to v1.137+ normally

Check your version: `snap list immich-distribution`

## Why This Change?

Immich removed TypeORM ([#20366](https://github.com/immich-app/immich/pull/20366)) requiring database schema upgrades that must be completed on versions v1.132.0-v1.136.0 before upgrading to v1.137+.

## Resources

- [v1.137.0 Release Notes](https://github.com/immich-app/immich/releases/tag/v1.137.0)
- [TypeORM Upgrade Documentation](https://immich.app/errors/#typeorm-upgrade)
