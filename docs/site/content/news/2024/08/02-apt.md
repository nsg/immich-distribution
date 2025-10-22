+++
template = "blog-post.html"
title = "Build apt-packages for the dependencies"
date = "2024-08-02 11:00:00"
path = "news/2024/08/02/build-apt-packages-for-the-dependencies"
authors = ["nsg"]
+++


![](/assets/build-time-apt.png)

The build time has been abysmal, over 40 minutes. Everything from Postgres to Python [was built in a single 658 lines snapcraft.yaml](https://github.com/nsg/immich-distribution/blob/1f29f0d5c3d4e528d9ae97bd0e03d4b3eacd7be3/snap/snapcraft.yaml) file. It has just sort of evolved over time.

This has been one of the classic: I do not have time to fix this, so I have lost time waiting for builds. I have tried to fix this twice, first with cache, and later on with snaps as a dependency. The first one introduced complexity, and the second one did not work that well, I had to fight the tooling.

I known that package the dependencies in deb packages was probably the smart thing to do, but I did not have the energy to figure out how to set it up, so I have stalled. But it's now done, I have created 14 different packages of `cgif`, `ffmpeg`, `haproxy`, `imagemagick`, `lego` ,`libde265`, `libheif`, `libraw`, `libvips`, `mimalloc`, `postgres`, `python`, `redis` and `x265`. You can read more about the repository [here](/build/dependencies).

## 10k feet overview

For the curious, I build the packages in clean OCI images (with Podman). The deb packages are created with [fpm](https://github.com/jordansissel/fpm) and I use [Aptly](https://www.aptly.info/) to manage the repository. I have also created a few bash scripts to "build", "add to repo" and "publish" to make life easier for future me.

The observant have seen that I'm down from 40 minutes to 17. I'm actually expected it to be lower but Immich takes a long time to build, and the resulting snap takes several minutes to compress. It's still over twice as fast. I also added a build cache, so if I only tweak the tests, it can reuse the cached snap package. That makes tweaking and troubleshooting much faster.

## Why did I do this now?

I had a test failure that only occurred on GitHub, it required a lot of rebuilds. I needed a distraction, and a distraction that also reduce the build time sounded like a good idea. This was also a good time to delay a release a little, this was the [purchase a license](https://github.com/immich-app/immich/discussions/11186) release and I preferred to wait a little before it [resolved it self](https://github.com/immich-app/immich/discussions/11313). There have also not been any breaking changes.
