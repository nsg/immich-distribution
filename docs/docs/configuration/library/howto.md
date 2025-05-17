# Storage How To

This page explains how to create different types of mounts to relocate or add library storage locations for Immich Distribution.

!!! Danger
    Incorrectly configuring mounts can potentially break your Immich installation or even your server.
    Please proceed with caution. Basic Linux administrative knowledge is assumed.

Locations that Immich can access and are suitable for storing images include `/var/snap/immich-distribution/common` and `/root/snap/immich-distribution/common`. The first location is already used by Immich Distribution, but you can create a subfolder there if desired.

!!! note "Future name collision"
    Choosing a folder under `/root/snap/immich-distribution/common` is recommended to reduce the risk of future name collisions with files created by the Snap package itself. If you prefer to use `/var/snap/immich-distribution/common`, ensure you pick a unique subfolder name.

## Examples

### Store all images and video on a large external drive

Assume you have a large, separate drive (e.g., `/dev/sda2`) attached to your system. It's formatted but not yet mounted. Follow these steps to move the `/var/snap/immich-distribution/common/upload` directory to this drive.

```shell title="Stop all Immich services"
sudo snap stop immich-distribution
```

```shell title="Temporary mount the new drive and move the existing data"
sudo mount /dev/sda2 /tmp
sudo mv /var/snap/immich-distribution/common/upload/* /tmp
sudo umount /tmp
```

```shell title="Mount /dev/sda2 to the correct location"
sudo mount /dev/sda2 /var/snap/immich-distribution/common/upload
```

```shell title="Start all Immich services"
sudo snap start immich-distribution
```

!!! warning "Please note"
    The `mount` command in the example above is temporary and will not persist across reboots. To make the mount permanent, you need to configure it in `/etc/fstab`, create a systemd `.mount` unit file, or use another method appropriate for your system.

### Store all images and video on a network attached NAS

This is also a common scenario. Follow the external drive guide above, but instead of mounting `/dev/sda2`, mount your NAS share.

Note that network-attached storage (NAS) is typically slower than local drives. To potentially improve performance, consider moving only the `/var/snap/immich-distribution/common/upload/library` directory (which contains large original files) to the NAS, while keeping smaller, frequently accessed assets like thumbnails and encoded videos on a local drive.

### How to access external libraries

If possible, mount the external library to a subfolder within the accessible locations, such as `/var/snap/immich-distribution/common/lunar-holiday` or `/root/snap/immich-distribution/common/lunar-holiday`.

```shell title="Mount the library (e.g., on /dev/sdb6) to a suitable location"
sudo mkdir /root/snap/immich-distribution/common/lunar-holiday
sudo mount /dev/sdb6 /root/snap/immich-distribution/common/lunar-holiday
```

Alternatively, you might want to add a specific existing folder as an external library. For instance, assume your holiday pictures are stored in `/data/lunar-holiday`. Immich cannot access this path directly due to the Snap sandbox. To resolve this, you need to bind mount `/data/lunar-holiday` to an accessible location, such as `/root/snap/immich-distribution/common/lunar-holiday`.

```shell title="Bind mount the library to a suitable location"
sudo mkdir /root/snap/immich-distribution/common/lunar-holiday
sudo mount --bind /data/lunar-holiday /root/snap/immich-distribution/common/lunar-holiday
```

Once bind-mounted, you can add the path `/root/snap/immich-distribution/common/lunar-holiday` to Immich as an external library via the web interface.

!!! warning "Please note"
    The `mount` commands in these examples are temporary and will not persist across reboots. You need to configure the mount in `/etc/fstab`, a systemd `.mount` unit file, or use another method appropriate for your system.

### Systemd bind mount example

Suppose you want to move `/var/snap/immich-distribution/common/upload/library` to another location, for example, to `/data/library` on a larger drive mounted at `/data`. This can be achieved with a bind mount. This example uses systemd mount units for persistence.

Create the following systemd mount unit file. Note that the filename is derived from the `Where` path; if you change this path, the filename must be updated accordingly.

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
    Note that the hyphen (`-`) in the path needs to be escaped as `\x2d` in the systemd unit filename. When typing the filename in a shell, you might need to escape the backslash itself (e.g., `\\x2d`) or use single quotes. One of the following will work:

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

``` title="Verify the mount unit file"
systemctl status var-snap-immich\\x2ddistribution-common-upload-library.mount
```

If there are no error messages, proceed by stopping the Immich services.

```shell title="Stop all Immich services"
sudo snap stop immich-distribution
```

```shell title="Move the existing data to its new location"
sudo mv /var/snap/immich-distribution/common/upload/library/* /data/library
```

``` title="Enable and start the systemd mount unit"
sudo systemctl enable --now var-snap-immich\\x2ddistribution-common-upload-library.mount
```

After the mount is active, both the original path and the new path should show the same content:

```bash
$ ls /var/snap/immich-distribution/common/upload/library
admin
$ ls /data/library
admin
$ 
```

All done! You can now start Immich again.

```shell title="Start all Immich services"
sudo snap start immich-distribution
```
