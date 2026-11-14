+++
template = "blog-post.html"
title = "Immich v3.4"
date = "2026-11-13"
path = "news/2026/11/13/immich-v3-4"
authors = ["nsg"]
+++

The snap is updated to Immich v3.4. See the [upstream release notes](https://github.com/immich-app/immich/releases/tag/v3.4.0) for what is new in Immich itself, including a long list of security fixes. This post covers what is different in the snap, and a few upstream changes you should know about before you update.

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
