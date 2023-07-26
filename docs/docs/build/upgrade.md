# Upgrade instructions

This page describe the upgrade process as a **developer** that I follow when I release a new version of Immich Distribution. If you like to contribute and help me with an update, follow this guide.

!!! Danger "This page is for developers"

    This page **do not** describe the update process done as a user. That's automatic! :partying_face: For update and user focused instructions see the [install page](/install/#updates).

## Open a tracking issue

Open a [New version issue](https://github.com/nsg/immich-distribution/issues/new/choose). Change `X.Y` to the relevant Immich version. Ignore patch releases (`1.23` instead of `1.23.4`). That will make it simpler if upstream releases a patch release. Immich do **not** follow strict [semantic versioning](https://semver.org/) but overall the patch releases are usually fixes and **minor** features that do not usually affect Immich Distribution.

## Bump Immich version

Run `make version-update`, this should update  `snap/snapcraft.yaml`, `parts/machine-learning/Makefile` and `patches/Makefile` with the new release version. The update script below will also validate that is is correctly done.

```yaml hl_lines="5"
  server:
    plugin: npm
    npm-node-version: "18.16.0"
    source: https://github.com/immich-app/immich.git
    source-tag: v1.64.0
    source-subdir: server
```

## Immich CLI

Because the CLI is included I always check for a [release of the CLI](https://github.com/immich-app/CLI/releases). Make sure to pick a release that existed when Immich was released so the versions match. Update `snapcraft.yaml` with the new release version.

```yaml hl_lines="5"
  cli:
    plugin: npm
    npm-node-version: "18.16.0"
    source: https://github.com/immich-app/CLI.git
    source-tag: v0.39.0
```

## Investigate the new release

!!! Tip "Hard to follow"

    If you are not experienced with snap packaging this can be hard to follow. If you are curious and like to learn just ask me! If this is not your cup of tea, there is also a few steps that do not require that much understanding about snaps.

I usually start by reading the [release notes](https://github.com/immich-app/immich/releases) to figure out if I need to do something special. Usually are pure code changes, like changes internally in the server, just fine. Changes to startup scripts, dependencies, paths, environment do possible require changes to this package.

Depending on the release size I have found it useful to look at code changes as well, at least so see what files the release touches. I have written a small tool to track important files called [update.sh](https://github.com/nsg/immich-distribution/blob/master/update.sh), use it like this:

```bash title="Compare released versions"
./update.sh old-tag new-tag # (1)
```

1. For example: `./update.sh v1.52.1 v1.53.0`

This script will diff files that I like to keep track on, for example:

* Dockerfiles - I keep track on then to detect changes to dependencies, changes to startup scripts and various things that _may_ affect the snap.
* Scripts - I do not use these scripts so I need to adapt whatever they to do my startup scripts
* Env-files and docker-compose-file - Detect relevant changes, like patch or environment changes that are required
* nginx config - I use HAProxy so I track changes to nginx to see if I need to apply them
* migrations - I track database changes to see if anything relevant has changed related to [database changes](https://github.com/nsg/immich-distribution/blob/master/src/etc/modify-db.sql) that the sync feature has done.

## Test it locally

!!! Note "This requires snapcraft"

    This requires that you have snapcraft installed and configured. I use multipass to build the package, but LXD should work just fine.

Now test it locally, I usually just run `make` that will build and install the snap. I try to trigger a few jobs from Immich Administration pages to make sure that the microservices and machine learning components work. I usually also upload a picture and/or a video to make sure that works. More advanced tests are done in CI and on a deployment that I run that follows the beta channel.

When I do the above I inspect all the logs to make sure everyting works, this is the command I usually use:

```
journalctl -fu snap.immich-distribution.*
```

Note that the package need to be installed for the `*` to expand properly.

## Make a Pull Request

I make a branch with a descriptive name and opens a pull request. This will trigger a CI run that builds the package and run a few simple tests agains the environment. If CI is happy, I will merge it to the `master` branch.

When that's done, the build service provided be Canonical will build the real snap that will end up in the store. It will be automatically signed and published to the edge channel.

## Release to beta

I release the revision in the `edge` channel to `beta` and refresh the installation on my beta server. I inspect the logs closely and make sure that the package works. This is a real production deploy so I can test Let's Encrypt.

## Relese to candidate

If everyting looks fine, I will release the same revision to `candidate`. My production deployment uses this channel. I will live with this release to make sure that everyting works.

## Release to stable

If everyting works for me, with no known problems, I will release this to the `stable` channel. I usually release this 2-3 days after candidate, but it may be faster if the mobile client is broken (that's unusual).

## The tracking issue

Keep it open for a few days for users to see, read and possible comment.

!!! Note "Repeat"

    It's not uncommon that Immich has released a new release at this point :man_facepalming: so let's start over!
