# External Libraries

Immich supports External Libraries, which are folders stored outside Immich's own internal library structure. You can read more about libraries in the [official documentation](https://immich.app/docs/features/libraries). You manage these libraries from Immich Web via a browser. However, the locations you can add are limited by the Immich Distribution sandbox.

## Sandbox

Immich Distribution is a Snap package, and Snap packages typically run inside a sandbox. This is a security feature, similar to how applications on phones are isolated. This sandbox limits where Immich Distribution can read and write data. To use external folders, you need to _mount_ them into a location accessible by the Snap.

Locations that Immich can access, suitable for external libraries, include subfolders within `/var/snap/immich-distribution/common` and `/root/snap/immich-distribution/common`. The first path is already used by Immich Distribution for its internal data, but you can create a unique subfolder there.

## Mount

You can make external storage accessible to Immich by either mounting a drive/partition directly to an allowed location or by using a bind mount for an existing directory. Standard symbolic links (symlinks) will not work due to the sandbox.

### Mount a drive, partition, volume or network share

Create a subfolder under one of the suitable locations (e.g., `/var/snap/immich-distribution/common/my-external-library` or `/root/snap/immich-distribution/common/shared-pictures`) and then mount your drive, partition, or network share to this newly created subfolder.

!!! note "Future name collision"
    Choosing a folder under `/root/snap/immich-distribution/common` is generally recommended to reduce the risk of name collisions with files the Snap package might create in `/var/snap/immich-distribution/common`. If you use `/var/snap/immich-distribution/common`, ensure your subfolder has a unique name.

### Use a bind mount

Alternatively, you can use a bind mount to make an existing folder accessible. For example, if your pictures are located in `/data/pictures` (which is outside the sandbox), you would bind mount `/data/pictures` to an accessible path like `/root/snap/immich-distribution/common/pictures`. Then, you add this latter path (`/root/snap/immich-distribution/common/pictures`) as an external library in Immich.

For detailed instructions on creating mounts, refer to [the storage how-to guide](howto.md).
