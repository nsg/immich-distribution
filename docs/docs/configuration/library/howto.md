# Storage How To

This page explains how to create different types of mounts to move or mount different library locations in to Immich Distribution.

!!! Danger
    This has the possibility to break your Immich installation, or even your server if you configure your mounts incorrectly.
    Please be careful, I assume basic Linux administrative knowledge.

Locations Immich can access, and are suitable for images are `/var/snap/immich-distribution/common` and `/root/snap/immich-distribution/common`. The first location is used by Immich Distribution already, but feel free to create a subfolder there if you like.

!!! note "Future name collision"
    I would choose a folder under `/root/snap/immich-distribution/common` to reduce the risk for future name collitions. If you like to use `/var/snap/immich-distribution/common`, pick a unique name.

## Examples

### Store all images and video on a large external drive

Let's assume that you have a large separate drive attached to your system under `/dev/sda2`, it's already formatted, but not mounted. Do this to move `/var/snap/immich-distribution/common/upload` to that drive.

```shell title="Stop all Immich services"
sudo snap stop immich-distribution
```

```shell title="Temporary mount the new drive and move the data"
sudo mount /dev/sda2 /tmp
sudo mv /var/snap/immich-distribution/common/upload/* /tmp
sudo umount /dev/sda2 /tmp
```

```shell title="Mount sda2 it to the corrent location"
sudo mount /dev/sda2 /var/snap/immich-distribution/common/upload
```

```shell title="Start all Immich services"
sudo snap start immich-distribution
```

!!! warning "Please note"
    Please note that in the example above, the mount-command will not persist cross reboot. You need to configure the mount in `/etc/fstab`, a systemd `.mount`-file or any other way relevant of your filesystem.

### Store all images and video on a network attached NAS

This is also a common option, follow the external drive guide above. Except, mount your NAS instead of `sda2`.

Note that network attached drives are usually considerable slower compated to local drives, a possible way to speed things up is to only move `/var/snap/immich-distribution/common/upload/library` to the NAS drive, keeping smaller folders like thumbs, encoded videos locally.

### How to access external libraries

If possible, mount the external library under the suitable locations `/var/snap/immich-distribution/common` or `/root/snap/immich-distribution/common`, for example `/root/snap/immich-distribution/common/lunar-holiday`.

```shell title="Mount the library on sdb6 to a suitable location"
sudo mkdir /root/snap/immich-distribution/common/lunar-holiday
sudo mount /dev/sdb6 /root/snap/immich-distribution/common/lunar-holiday
```

Another scenario is that you only like to add a specific folder as a library. Let's assume that your holiday pictures are stored under `/data/lunar-holiday`. Immich can't access that patch due the snap sandbox. To solve that, we need to bind mount `/data/lunar-holiday` to a suitable location like `/root/snap/immich-distribution/common/lunar-holiday`.

```shell title="Bind mount the library to a suitable location"
sudo mkdir /root/snap/immich-distribution/common/lunar-holiday
sudo mount --bind /data/lunar-holiday /root/snap/immich-distribution/common/lunar-holiday
```

All done, now add the path `/root/snap/immich-distribution/common/lunar-holiday` to Immich as an external library.

!!! warning "Please note"
    Please note that in the examples above, the mount-commands are not persist cross reboots. You need to configure the mount in `/etc/fstab`, a systemd `.mount`-file or any other way relevant of your filesystem.

### Systemd bind mount example

Let's assume that you like to move `/var/snap/immich-distribution/common/upload/library` to another drive, our large drive is located at `/data` and that we have a folder inside it at `/data/library` that should contain our library data. This is done with a bind mount, in this example I use systemd mounts.

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

!!! Info "Figure out a correct filename"
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
