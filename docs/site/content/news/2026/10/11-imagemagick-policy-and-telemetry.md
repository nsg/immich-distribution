+++
template = "blog-post.html"
title = "Stricter ImageMagick Policy and No ML Telemetry"
date = "2026-10-11"
path = "news/2026/10/11/imagemagick-policy-and-telemetry"
authors = ["nsg"]
+++

The v3.3.0 release of the snap includes a few packaging changes worth knowing about. See the upstream release notes for [v3.3.0](https://github.com/immich-app/immich/releases/tag/v3.3.0) for what is new in Immich itself.

## Stricter ImageMagick policy

This is security hardening that brings the snap in line with upstream: it now ships the same ImageMagick security policy as the upstream Docker image. Until now the package used ImageMagick's default policy, which restricts nothing. The new policy blocks external programs, the scripting, network and text coders, and reading files through indirect or relative paths, so a crafted upload can't trick ImageMagick into reading local files or fetching URLs.

Immich only uses ImageMagick as a fallback for formats that libvips can't read on its own. Common formats like JPEG, PNG, HEIC, WebP and RAW never reach it, so most libraries won't notice any difference.

There is one behavior change: the policy refuses to follow symlinks. If a file is itself a symlink, for example in an external library, and it is in a format that needs the ImageMagick fallback, it will no longer get a thumbnail. Symlinked directories are not affected. Replace the symlink with the real file if you run into this.

{% admonition(type="note", title="Affected by this?") %}
If the stricter policy breaks something for you, please let me know in an [issue](https://github.com/nsg/immich-distribution/issues).
{% end %}

## Machine learning telemetry disabled

Upstream updated onnxruntime, the library that runs the machine learning models, to a version that collects usage telemetry by default on Linux and queues it for upload to Microsoft. The snap opts out of this, so the machine learning service does not collect or send it.

## Updated image libraries

The bundled libheif and LibRaw were updated to match upstream (1.23.5 and 0.22.2).
