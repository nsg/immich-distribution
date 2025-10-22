+++
template = "blog-post.html"
title = "Release v1.88"
date = "2023-07-30"
path = "news/2023/07/30/release-v188"
authors = ["nsg"]
+++


There has been 17 releases since the last news post. The automatic issues and pull requests have simplified the release process and a few have been more or less fully automatic.

{% admonition(type="danger", title="BREAKING CHANGE: This release removes the bundled CLI command") %}
The [Immich CLI](https://github.com/immich-app/CLI) have been included in the package since the begining. It has been removed in this release.
{% end %}

I have included [Immich CLI](https://github.com/immich-app/CLI) in the package under `immich-distribution.cli` since the beginning. I initally added it for the upload functionality in the [sync feature](/configuration/sync/) but choose to expose it to users via `immich-distribution.cli`.

The bundled CLI has not been that useful, it's restricted from where it can read due the sandbox and I never found it useful myself. I usually install the cli manually outside anyway. The CLI has since five days ago been deprecated in favour of a new CLI that's included in Immich normal repository.

{% admonition(type="info", title="Install Immich CLI") %}
You need to install the new CLI manually, upstream documents it [here](https://immich.app/docs/features/command-line-interface). There is also a excellent 3rd party cli called [immich-go](https://github.com/simulot/immich-go) that may be easier to install, and have several interesting features.
{% end %}

I have implemented the file upload logic myself in Python (with inspiration from the [documentation](https://immich.app/docs/guides/python-file-upload)). I initally avoided this because I thought the API would change a lot and it would be easier to call the official command line utility. The tests use the same logic to if this fails, the automatic tests should catch it.
