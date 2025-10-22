+++
template = "blog-post.html"
title = "Release v1.66"
date = "2023-07-09"
path = "news/2023/07/09/release-v166"
authors = ["nsg"]
+++


[Issue #48](https://github.com/nsg/immich-distribution/issues/48) - (Released to beta 2023-07-09)

I had to adapt my patched update dialog box. Upstream had refactored the code so I rebased on top of that to create a cleaner diff. At first glance I thought that but the default ffmpeg parameters had changed and that required me to update to a newer version of ffmpeg.

## Changes

* Immich v1.66.1
* FFmpeg updated from 4.2.7 (distributed by Canonical) to 6.0 (distributed by [John Van Sickle](https://johnvansickle.com/ffmpeg/), officially [promoted by the FFmpeg project](https://ffmpeg.org/download.html)).
