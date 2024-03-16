# External Libraries

Immich has support for External Libraries. They are folders stored outside Immich own internal library. You can read more about libraries on the [official documentation](https://immich.app/docs/features/libraries). You manage them from Immich Web via a browser, but the available locations are limited due Immich Distributions sandbox.

## Sandbox

Immich Distribution is a snap package, and snap packages are typically running inside a sandbox. That's a security feature most known from phones where an application is isolated from other applications. That limits where Immich Distribution can read and write data, to work around that you need do _mount_ your data to the correct location.

Locations Immich can access, and are suitable for images are `/var/snap/immich-distribution/common` and `/root/snap/immich-distribution/common`. The first location is used by Immich Distribution already, but feel free to create a subfolder there if you like.

## Mount

You can work around the sandbox by either mounting the new drive/mount directly to the correct spot, or, use a bind mount. Links like symlinks will not work!

### Mount a drive, partition, volume or network share

Make a subfolder under one of the suitable locations, for example `/var/snap/immich-distribution/common/my-library-pictures` or `/root/snap/immich-distribution/common/pictures` and mount it to that location.

!!! note "Future name collision"
    I would choose a folder under `/root/snap/immich-distribution/common` to reduce the risk for future name collitions. If you like to use `/var/snap/immich-distribution/common`, pick a unique name.

### Use a bind mount

You can also bind mount a folder from one path of the filesystem to another. So let's assume that your pictures are located in `/data/pictures`. You need to bind mount that to `/root/snap/immich-distribution/common/pictures` and add the later path to Immich.

For more information about mounts see [the storage how to](howto.md).
