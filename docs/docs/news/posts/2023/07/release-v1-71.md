---
date: 2023-07-30
authors: [nsg]
categories:
  - Release
---

# Release v1.71

!!! Note "Relese updates"
    From this point on forward, I will omit news posts that says nothing more interesting than "new version".
    If you like to follow my release process [the new-version tag](https://github.com/nsg/immich-distribution/issues?q=is%3Aissue+label%3Anew-version+) is probably more interesting.

[This release](https://github.com/nsg/immich-distribution/issues/74) was the first one done by GitHub Action Automations. I have written a script that runs a few times a day for new upstream releases. If there is a release, an Issue is created like [this one](https://github.com/nsg/immich-distribution/issues/74), and a pull request is created [like this one](https://github.com/nsg/immich-distribution/pull/81). All the output that I normally executed on my computer is added to the PR.

This pattern follows what I have been doing manually for a few months, this is just another tooling improvement that I have implemented in this release utilizing the improved tests and version bump scripts.
