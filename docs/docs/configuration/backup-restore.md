# Backup and Restore

A backup and restore command is bundled as part of the Snap package. These are simple shell scripts that wrap `psql` (for database operations) and `tar` (for file archiving). They are included for convenience.

!!! Note "Backup recommendations"

    On an installation with many pictures, the asset archive (`.tar` file) can become impractically large. It is generally recommended to use these tools to back up only the database and to back up the asset files directly using your preferred backup software.

    The `-a` (assets) option is primarily intended for smaller installations or for quickly restoring test instances.

## Manual Backup

```
immich-distribution.backup [-d] [-D <name>] [-a] [-l]

-d           Backup database (timestamp-based)
-D <name>    Backup database with a custom name
-a           Backup assets (images, videos, ...)
-l           List all available backups
```

The recommended backup strategy is to perform a database backup using the `-d` option, and then manually back up the asset directories. These are typically located at `/var/snap/immich-distribution/common/upload/{==library==}`, `/var/snap/immich-distribution/common/upload/{==upload==}` (for external library uploads if applicable), and `/var/snap/immich-distribution/common/upload/{==profile==}`.

## Automatic backup

An included backup service can be enabled with the command below. This service will perform a daily database backup and retain these backups for one week.

```
sudo snap set immich-distribution backup-database-daily=true
```

Backups are scheduled to occur daily at `01:00` server time. Backups older than one week are automatically removed.

## Restore

```
immich-distribution.restore -y [-d <database-backup>] [-a <assets-backup>]

-y           Confirm destructive overwrite
-d <FILE>    Restore a database backup
-a <FILE>    Restore assets from an assets backup
```

!!! danger
    Note that restoring will **DESTROY** and **OVERWRITE** your current Immich installation data!
