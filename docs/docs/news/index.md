# News

This page list latest news and announcements related to Immich Distribution.

## Release v1.70

[Issue #56](https://github.com/nsg/immich-distribution/issues/56) - (Released to beta 2023-07-27)

Update Immich version

## Release v1.69

[Issue #55](https://github.com/nsg/immich-distribution/issues/55) - (Released to beta 2023-07-27)

The last release contains improved update tooling, this release contains [improved tests](/build/tests/). This should help me find problems earlier, and shorten the amount of manual testing that I need to do.

## Release v1.68

[Issue #53](https://github.com/nsg/immich-distribution/issues/53) - (Released to beta 2023-07-26)

Bumped the version, improved tooling around my [update modal patch](/build/patches/) because it had changed in upstream again. This should make it easier for me to update this in the future if the file changes.

!!! Info Vaccation
    The update was delayed a little due my vacation and the above patch made this a tiny bit more complex.

## Release v1.67

[Issue #51](https://github.com/nsg/immich-distribution/issues/51) - (Released to beta 2023-07-17)

This was a simple release, I have bumped the version to the latest Immich relese.

### Changes

* Immich v1.67.2

## Release v1.66

[Issue #48](https://github.com/nsg/immich-distribution/issues/48) - (Released to beta 2023-07-09)

I had to adapt my patched update dialog box. Upstream had refactored the code so I rebased on top of that to create a cleaner diff. At first glance I thought that but the default ffmpeg parameters had changed and that required me to update to a newer version of ffmpeg.

### Changes

* Immich v1.66.1
* FFmpeg updated from 4.2.7 (distributed by Canonical) to 6.0 (distributed by [John Van Sickle](https://johnvansickle.com/ffmpeg/), officially [promoted by the FFmpeg project](https://ffmpeg.org/download.html)).

## Release v1.65

[Issue #46](https://github.com/nsg/immich-distribution/issues/46) - (Released to beta 2023-07-09)

!!! Info
    I have done 12 releases :partying_face: of Immich Distribution since I started this project back in March, that's almost 4 months and about 3 releases per week! Updates have gotten easier but I have had a few annoying ones that took me quite a lot of time to figure out. I have also been away for a week and had several releases to catch up with when I got back.

This has been one of these easy releases with just a version bump needed, see the [release notes](https://github.com/immich-app/immich/releases/tag/v1.65.0). I mainly created this post to get started with a news section on the brand new project and documentation site. I hope to publish short release notes with relevant news and changes related to Immich Distribution.

### Changes

* Documentation moved, and expanded, to this site
* Immich v1.65.0
