+++
template = "blog-post.html"
title = "Immich v3.4"
date = "2026-11-13"
path = "news/2026/11/13/immich-v3-4"
authors = ["nsg"]
+++

This release upgrades the snap to Immich v3.4.0. See the upstream release notes for [v3.4.0](https://github.com/immich-app/immich/releases/tag/v3.4.0) for what is new in Immich itself, including a long list of security fixes. This post covers what is different in the snap, and a few upstream changes you should know about before you update.

## First start

The update adds a few indexes to the database. Immich builds them before it starts, so on a large library the first start after the update may take a little longer than usual; let it run.

## Newer machine learning models

Upstream now selects the `v2` model exports in its default Docker Compose file. They run faster on the CPU, and the snap follows upstream and uses them by default. The first time the machine learning service runs after the update, it downloads the `v2` versions of your models. Existing smart search and face data keeps working, nothing needs to be re-indexed.

If you prefer to keep the original exports, set the new `ml-model-revision` option, see [Machine Learning](/configuration/machine-learning/):

```bash
sudo snap set immich-distribution ml-model-revision=main
```

The original models stay in the cache folder under `/var/snap/immich-distribution/common/cache`; the `v2` models are stored in a `v2` subfolder of each model folder. If you stay on `v2`, you can delete the other subfolders of each model folder to free some disk space.

## JPEG XL thumbnails

Immich can now generate thumbnails and previews in the JPEG XL format, an option under Administration, Settings, Image Settings. The image libraries in the snap are now built with JPEG XL support, matching the upstream Docker image. The default format is unchanged.

## Backups are not supported

Immich v3.4 adds a new beta backup feature, FUTO Backups, under Administration, Backups. It is built on `restic`, which the snap does not ship, so the feature does not work in the snap. I have no good way to test this feature, and I would rather not give the impression that your data is backed up when it is not. Keep using the [database backups and your own file backups](/configuration/backup-restore/).

## Symlinks in external libraries

External library scans no longer follow symlinks. This is an upstream security fix. If an external library contains symlinked folders or files, new files behind them are no longer imported, and assets that were imported through a symlink may be marked offline on the next scan. Mount or move the real folders into the library path instead.

## Faster database backups

The snap now includes `pigz`, which Immich uses to compress database backups on several CPU cores.
