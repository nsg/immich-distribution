# Storage Locations

Immich uses libraries to store assets, the default library is where your files ends up, unless you change the configuration. You can read more about libraries on the [official documentation](https://immich.app/docs/features/libraries). You manage them from Immich Web via a browser, but the available locations are limited due Immich Distributions sandbox.

By default Immich stores all files in `/var/snap/immich-distribution/common`, maybe you like to move your library to a larger storage drive, or a faster one.

## Sandbox

Immich Distribution is a snap package, and snap packages are typically running inside a sandbox. That's a security feature most known from phones where an application is isolated from other applications. That limits where Immich Distribution can read and write data, to work around that you need do _mount_ your data to the correct location.

## Directory layout

All folders are under `/var/snap/immich-distribution/common`, I will shorten it to `$C` below to save space. A path written as `$C/upload` is refering to `/var/snap/immich-distribution/common/upload`. This is not a complete list, I'm focusing on a few common use cases.

### $C/upload

> "Move everting to a large drive / network share"

Immich Server stores all assets here, this contains **all your media** including originals, and transcoded videos and thumbnails. This is probably the most common location to mount to a larger drive/location, or for a network mount from a NAS.

### $C/upload/library

> "Only move the large original assets, but keep frequently accessed files locally"

If you have not moved the entire `$C/upload` it may be useful to move the library folder. This folder contains all your uploaded originals. The exact proportions of the different storage locations depends on your media. But expect this to be the largest folder. For example on my installation, library stands for around 75% of all used disk space.

### $C/upload/thumbs and $C/upload/encoded-video

> "Move thumbs and other assets to faster drive to speed things up"

If you have an smaller NVME drive that do not fit your entire library, it could be useful to move these to a faster drive. This is probably the assets your browser or phone is accessing when browsing your library.

## How to move the folders

From Immich Distributions point of view all folders need to stay in `/var/snap/immich-distribution/common`, you can't move folders, but you can move the data with a mount. Links (like symlinks) will not work. For more information about mounts see [the storage how to](howto.md).
