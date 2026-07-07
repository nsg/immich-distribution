+++
template = "blog-post.html"
title = "Immich v3"
date = "2026-07-07"
path = "news/2026/07/07/immich-v3"
authors = ["nsg"]
+++

Immich v3 is here, and this release upgrades the snap from v2.7.5 to v3. It's a major upstream release; see the upstream release notes for [v3.0.0](https://github.com/immich-app/immich/releases/tag/v3.0.0) for the full list of changes, including API and third-party client changes that I won't repeat here.

## What's new

The headline features are **Workflows**, a preview feature for automating actions in your library built on the new plugin system, and **HLS real-time video transcoding**, an experimental opt-in feature that streams video without waiting for a full transcode. Upstream considers HLS experimental, and I have not tested it as part of this package — but if you try it out and it works, I would be happy to hear about it in an [issue](https://github.com/nsg/immich-distribution/issues). For HLS to work on videos uploaded before v3, re-run the Metadata Extraction job from the admin Jobs page.

The legacy built-in sync service was removed with this upgrade — see the [dedicated post](/news/2026/07/06/sync-service-removed/) for details and migration options.

## Things to watch out for

**Machine learning now requires a x86-64-v2 CPU** (SSE4.2/POPCNT, roughly 2009 or newer) because upstream moved to numpy 2.4. On very old CPUs, ML features like smart search and face detection will crash after this upgrade — the rest of Immich keeps working.

**OAuth over plain `http://`** (no TLS) is disallowed by default in v3. The upgrade automatically enables the new `oauth.allowInsecureRequests` setting if your issuer URL starts with `http://`, but if OAuth stops working after the upgrade, check "Allow insecure requests" under the OAuth settings in the Immich admin panel.
