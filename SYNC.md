# Sync

This script will synchronize changes in `/var/snap/immich-distribution/common/sync/b281b4f0-a911-49b1-abf2-bf5eeecedb32` with the Immich user with a matching `USER ID`. You can find your ID in Account Settings.

The service supports the following events:

| Event | Action |
| ----- | ------ |
| File added to `sync/b281b4f0...` | File imported to Immich as user `b281b4f0...` |
| File removed from `sync/b281b4f0...` | File deleted from Immich from user `b281b4f0...` |
| File modified in `sync/b281b4f0...` | Not sure what to do here. Immich has no interface to modify an asset. Should I delete the old one and upload a new image? Metadata like albums will be lost if I do this. At the moment this event is ignored.
| Asset removed from `b281b4f0...` in Immich | File deleted from `sync/b281b4f0...` |

## Limitations

* The snap package can't read and write outside `/var/snap/immich-distribution/`, so you can't symlink the folder `sync/b281b4f0...`, but bind mounts should work.
* `fswatch` is used to listen for changes. Remote file system mounts will probably not emit these events.

## Useful Ideas

* Share `sync/b281b4f0...` via Synthing to add/remove files to Immich.
* Synchronize `sync/b281b4f0...` via the Nextcloud client to connect a folder.
* ... or just mount a large folder of images for Immich to ingest and manage.

## Usage

1. Generate a API Key under Account Settings
2. Run `sudo snap set immich-distribution sync="BuIbUtIdwisuxanRyighCenmykongIc9"` (separate multiple keys with a space)
3. Place files in `/var/snap/immich-distribution/common/sync/{USER ID}`
