# Backup and Restore

There is a backup and import command bundled as part of the snap. This is simple shell scripts wrapping `psql` and `tar`. They are included for your convenience.

!!! Note "Backup recommendations"

    On a real install with a lot of pictures the tar-file will be unusable large. It's recommended to only backup the database with these tools and manually backup the files directly with your backup software of choice.

    The `-a` option is here mainly for smaller installations and they can be useful to quickly restore test instances.

## Manual Backup

```
immich-distribution.backup [-d] [-a] [-l]

-d	Backup database
-a	Backup assets (images, videos, ...)
-l  List backups
```

The recommended way to backup Immich is to do a database backup with `-d`, and then manually backup the assets directly from `/var/snap/immich-distribution/common/upload/{==library==}`, `/var/snap/immich-distribution/common/upload/{==upload==}` and `/var/snap/immich-distribution/common/upload/{==profile==}`.

## Automatic backup

There are an included backup service that you can enable with the command below. It will run a daily database backup and keep them for a week.

```
sudo snap set immich-distribution backup-database-daily=true
```

Backups will occur every night at `01:00`. Backups older than a week should be removed automatically.

## Import / Restore

```
immich-distribution.import [-d database-backup] [-a assets-backup]

-d	FILE   Import a database backup
-a	FILE   Import assets (images, videos, ...) from an asset backup
```

!!! danger
    Note that this will **DESTROY** and **OVERWRITE** your current install!
