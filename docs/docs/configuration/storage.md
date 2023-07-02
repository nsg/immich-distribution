# Storage

!!! Danger
    This has the possibility to break your Immich installation, or even your server if you configure your mounts incorrectly. Please be careful, I assume basic Linux administrative knowledge.

By default Immich stores all files in `/var/snap/immich-distribution/common`, maybe you like to move your library to a larger storage drive, or a faster one. This page will explain what files are stored where, and how to move them to a new location with **bind mounts**.

??? Note "A note about removable-media"
    Snapd provides an interface called `removable-media` to read data from `/mnt`, `/media` and `/run/media`, it's possible for me to add these interfaces to the snap, and modify all scripts and tools to support multiple locations.
    
    It would not be that hard to do this, the problem is that Immich do not support that we move files around so this should only be possible to do on new installations, or alternatively I could write a migration script... doable, but it would be not to easy to test and maintain and be a source of bugs.

    I will instead document how to do this from the "outside", outside the sandbox.

## Directory layout

All folders are under `/var/snap/immich-distribution/common`, I will shorten it to `$C` below to save space. A path written as `$C/upload` is refering to `/var/snap/immich-distribution/common/upload`. This is not a complete list, I have only listed directories that contains images and videos who has the potential to grow in size and may be useful to move to another storage location.

| Path { style="width: 15em" } | Description | Sample |
| ---------------------------- | ----------- | ---- |
| `$C/backups` | Backups triggered with [immich-distribution.backup](/configuration/backup-restore) will be stored here. This will be empty unless you use this function. | 11K |
| `$C/sync` | Files montitored by the sync feature, this mount **must** support inotify. This will be empty unless you use this feature. | 23G |
| `$C/upload` | Immich Server stores all assets here, this contains **all your media** including originals, and transcoded videos and thumbnails. | 235G |
| `$C/upload/upload` | Temporary upload location. When you upload a picture it's temporarily stored here. It's then moved to library. Failed files _may_ still linger in this folder. | 109M |
| `$C/upload/library` | This is the location of all your images and videos! | 171G |
| `$C/upload/thumbs` | Thumbnails generated from images and videos optimized for consumption in the web and mobile clients. | 23G |
| `$C/upload/encoded-video` | Encoded videos, re-encoded from your originals optimized for consumption in the web and mobile clients. | 27G |

I have provided a sample disk usage with 56k pictures and 800 videos. If you like to "move all large files" in a typical Immich installation to a separate drive I would probably move `$C/upload`, alternatively `$C/upload/library`.

## Relocate library to another drive with a bind mount

Let's assume that you like to move `$C/upload/library` to another drive, our large drive is located at `/data` and that we have a folder inside it at `/data/library` that should contain our library data. This is done with a bind mount, in this example I use systemd mounts.

Create the following mount-file. Note that the filename is based on `Where`, if you change this patch, this file need to be renamed as well.

```toml title="/etc/systemd/system/var-snap-immich\x2ddistribution-common-upload-library.mount" 
[Unit]
Description=Bind Mount Immich Library

[Mount]
What=/data/library
Where=/var/snap/immich-distribution/common/upload/library
Type=none
Options=bind
TimeoutSec=5

[Install]
WantedBy=multi-user.target
```

!!! Warning
    Note that (`\x2d`) can cause problems, you need to double escapt it as `\\x2d` alternatively surround it with a single quote (`'`). One of the following will work:

    ```
    $EDITOR {=='==}/etc/systemd/system/var-snap-immich\x2ddistribution-common-upload-library.mount{=='==}
    ```

    ```
    $EDITOR /etc/systemd/system/var-snap-immich{==\==}\x2ddistribution-common-upload-library.mount
    ```

??? Info "Figure out a correct filename"
    There is a built in command called `systemd-escape` that you can use to generate a correctly escaped string.

    ```bash
    systemd-escape -p --suffix=mount "/var/snap/immich-distribution/common/upload/library"
    ```

``` title="Make sure that the file is valid"
systemctl status var-snap-immich\\x2ddistribution-common-upload-library.mount
```

If you see no error messages, let's start by shuting down Immich services.

```shell title="Stop all Immich services"
sudo snap stop immich-distribution
```

```shell title="Move the data to it's new location"
sudo mv /var/snap/immich-distribution/common/upload/library/* /data/library
```

``` title="Enable and start the mount"
sudo systemctl enable --now var-snap-immich\\x2ddistribution-common-upload-library.mount
```

Both locations should now contain the same files

```bash
$ ls /var/snap/immich-distribution/common/upload/library
admin
$ ls /data/library
admin
$ 
```

All done, start Immich again!

```shell title="Start all Immich services"
sudo snap start immich-distribution
```

## Relocate the entire upload folder with a bind mount

!!! Warning
    This section assumes that you have read and understood the above section.

Stop Immich, move data to it's new location. Use this unitfile, note that the filename has changed, and `What` and `Where`. Enable and start it, and finally Immich.

```toml title="/etc/systemd/system/var-snap-immich\x2ddistribution-common-upload.mount" 
[Unit]
Description=Bind Mount Immich Folder

[Mount]
What=/data
Where=/var/snap/immich-distribution/common/upload
Type=none
Options=bind
TimeoutSec=5

[Install]
WantedBy=multi-user.target
```
