+++
template = "blog-post.html"
title = "Immich v3.4"
date = "2026-11-14"
path = "news/2026/11/14/immich-v3-4"
authors = ["nsg"]
+++

The snap is updated to Immich v3.4. See the [upstream release notes](https://github.com/immich-app/immich/releases/tag/v3.4.0) for what is new in Immich itself, including a long list of security fixes. This post covers what is different in the snap, and a few upstream changes you should know about before you update.

## Empty asset backups since September

Since around the second week of September 2026, `immich-distribution.backup -a` has created empty asset archives while reporting success. Only the asset archives were affected; database backups, both the snap's and Immich's own, worked as usual. A security update to `tar` in the Ubuntu base made it incompatible with the snap's confinement. This update fixes it, and backup and restore are now tested for every release.

As the [backup documentation](/configuration/backup-restore/) recommends, back up the database with the snap and your photos directly with your own backup software. The `-a` option is meant for small installations and test instances.

## Newer machine learning models

Like upstream Immich, the snap now uses the faster `v2` model exports, and this update moves your installation to them. The new models are downloaded automatically. They have no new hardware or system requirements, so there is no reason to expect problems, and existing smart search and face data keeps working without re-indexing. If you run into issues, or prefer the original models, switch back to `main`, see [Machine Learning](/configuration/machine-learning/) for details:

```bash
sudo snap set immich-distribution ml-model-revision=main
```

The old models stay in `/var/snap/immich-distribution/common/cache`. On `v2`, you can free disk space by deleting everything except the `v2` subfolder in each model folder.

## JPEG XL thumbnails

Immich can now generate thumbnails and previews in the JPEG XL format, an option under **Administration ➔ Settings ➔ Image Settings**. The image libraries in the snap are now built with JPEG XL support, matching the upstream Docker image. The default format is unchanged.

## FUTO Backups are not supported

Immich v3.4 adds a new beta backup feature, FUTO Backups, under **Administration ➔ Backups**. The snap does not support it. I have no good way to test it, and I would rather not offer you a backup solution that may be broken. Keep using the [database backups and your own file backups](/configuration/backup-restore/).

If you would like FUTO Backups to work in the snap, [open an issue](https://github.com/nsg/immich-distribution/issues) and we can discuss the options.

## Symlinks in external libraries

External library scans no longer follow symlinks. This is an upstream security fix. If an external library contains symlinked folders or files, new files behind them are no longer imported, and assets that were imported through a symlink may be marked offline on the next scan. Mount or move the real folders into the library path instead.

## Metrics address in v3.4.2

From v3.4.2, upstream Immich serves Prometheus metrics on the same address as Immich itself. In the snap that is localhost, as Immich runs behind HAProxy, so other machines would no longer reach the metrics. The snap diverges a little from upstream here and keeps `0.0.0.0` (all IPv4 interfaces) as the default, the same as in v3.4.0 and v3.4.1. This is not a breaking change and you do not need to do anything.

The address is now configurable with `metrics-bind-address`, see [Metrics](/configuration/metrics/) for details. For example, to only allow access from the server itself:

```bash
sudo snap set immich-distribution metrics-bind-address=127.0.0.1
```

Only IPv4 addresses work for now. Metrics over IPv6, which worked up to v3.3, need an [upstream fix](https://github.com/immich-app/immich/pull/33488) that is not yet released.
