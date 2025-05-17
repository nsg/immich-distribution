# Storage Locations

Immich uses libraries to store assets. By default, your files end up in the default library unless you change the configuration. You can read more about libraries in the [official documentation](https://immich.app/docs/features/libraries). You manage libraries from Immich Web via a browser, but the available storage locations are limited due to the Immich Distribution sandbox.

By default, Immich stores all files in `/var/snap/immich-distribution/common`. You might want to move your library to a larger or faster storage drive.

## Sandbox

Immich Distribution is a Snap package, and Snap packages typically run inside a sandbox. This is a security feature, similar to how applications on phones are isolated from each other. This sandbox limits where Immich Distribution can read and write data. To work around this, you need to _mount_ your desired storage location to an accessible path.

## Directory layout

All relevant folders are under `/var/snap/immich-distribution/common`. For brevity, this path will be referred to as `$C` below. For example, a path written as `$C/upload` refers to `/var/snap/immich-distribution/common/upload`. This is not an exhaustive list but focuses on common use cases.

### $C/upload

> "Move everything to a large drive / network share"

Immich Server stores all assets here. This includes **all your media**: originals, transcoded videos, and thumbnails. This is likely the most common location to mount to a larger drive or a network share (e.g., from a NAS).

### $C/upload/library

> "Only move the large original assets, but keep frequently accessed files locally"

If you haven't moved the entire `$C/upload` directory, it might be useful to move just the library folder. This folder contains all your original uploaded media. The exact storage proportions will depend on your media collection. However, expect this to be the largest folder. For example, on my installation, the library accounts for approximately 75% of the total disk space used.

### $C/upload/thumbs and $C/upload/encoded-video

> "Move thumbs and other assets to faster drive to speed things up"

If you have a smaller NVMe drive that cannot fit your entire library, moving these assets to the faster drive could be beneficial. These are likely the assets your browser or phone accesses most frequently when browsing your library.

## How to move the folders

From Immich Distribution's perspective, all these folders must reside within `/var/snap/immich-distribution/common`. You cannot simply move these folders; instead, you must use mounts to relocate the data. Standard symbolic links (symlinks) will not work due to the sandbox. For detailed instructions on creating mounts, see [the storage how-to guide](howto.md).
