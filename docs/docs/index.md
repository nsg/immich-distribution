---
title: About
hide:
  - navigation
---

# About Immich Distribution

![Immich Distribution Logo](/assets/immich-dist.png){ align=right .img-scale }

These pages contains documentation related to the [snap](https://snapcraft.io/docs) package [immich-distribution](https://snapcraft.io/immich-distribution). It's based on [Immich](https://immich.app/), a self hosted [Google Photos](https://en.wikipedia.org/wiki/Google_Photos) replacement in early development. The package is inspired of the official Immich images. It will be **similar, but not identical** with the official Docker-based installation. Extra tools and customizations are included.

## Expectations

Do not expect me to release updates the same day as the upstream Immich release. Immich is a really fast moving project and it's not uncommon that it takes me a few days to find the time to prepare a release. When Immich releases an update, I will build and push an update and try it out for a few days before I release it to the stable channel. You can track update progress over at [GitHub](https://github.com/nsg/immich-distribution/issues?q=is%3Aissue+is%3Aopen+label%3Anew-version).

![Flowers in a box, in a room. Generated with Midjourney](/assets/room.png)

## Support

The [GitHub project page](https://github.com/nsg/immich-distribution) is also the place where you can suggest ideas, ask questions, report bugs and overall keep yourself informed on what's going on with the project.

## History

I deployed the [Docker based images](https://immich.app/docs/install/docker-compose) on a server initally, it worked just fine[^1]. But Immich is fast moving, with updates several times a week is not uncommon. I know that I'm lazy be nature and I have really enjoyed running [Nextcloud as a snap package](https://snapcraft.io/nextcloud) for several years. This has been a zero care experience for me, it just updates in the background automatically. There was no solution like that for Immich, so I created Immich Distribution. Sure, this is more job for me to run compared to "just run the docker images" but now, **you** and hundreds of people have a super easy deployment option.

[^1]: I had a little trouble with Docker/Podman, bit that's not a fault of Immich and out of scope of this discussion.

## Contribute

I like to keep upstream Immich a thriving project, so if you have the possibility please consider to [support the project](https://immich.app/docs/overview/support-the-project). If you like to support *this* project. Use the software, report issues, write suggestions, contribute with bugfixes and help me to test new releases. A simple :star: or :thumbsup: at the right place will also keep me motivated. See the projects [GitHub repository](https://github.com/nsg/immich-distribution) for more information.
