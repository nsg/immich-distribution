+++
title = "Upgrade instructions"
+++

# Upgrade instructions

This page describe the upgrade process as a **developer** that I follow when I release a new version of Immich Distribution. If you like to contribute and help me with an update, follow this guide.

{% admonition(type="danger", title="This page is for developers") %}
This page **do not** describe the update process done as a user. That's automatic! :partying_face: For update and user focused instructions see the [install page](/install/#updates).
{% end %}

## Tracking issue

A GitHub Action monitors Immich releases and should automatically create a new version issue for major and minor releases (`1.23` instead of `1.23.4`). This issue tracks all pull requests related to this release. This is also a place where developers and users can communicate.

Immich do **not** follow strict [semantic versioning](https://semver.org/) but overall the patch releases are usually fixes and **minor** features that do not usually affect Immich Distribution.

## Bump Immich version

A GitHub Action will automatically create an PR with relevant files.
The pull request will be containing various information. A human needs to verify the state and if it looks good merge the PR.

{% admonition(type="note", title="Multiple versions") %}
If there are different versions like 1.23 or 1.24, it's important to understand the process. Each minor version, denoted as 1.xx, will have its own tracking issue. If there happen to be several tracking issues open at once, only the earliest or oldest one is used for the pull request. It also ensures that there are never two PRs open at the same time. This approach not only minimizes the need for rebasing but also significantly cuts down the risk of merge conflicts.

Furthermore, by default, the logic employs the latest release of the oldest open tracking issue as the new version. However, if this latest release is already mentioned in the VERSION file, then the next tracking issue in line is used.
{% end %}

## Investigate the new release

{% admonition(type="tip", title="Hard to follow") %}
If you are not experienced with snap packaging this can be hard to follow. If you are curious and like to learn just ask me! If this is not your cup of tea, there is also a few steps that do not require that much understanding about snaps.
{% end %}

I usually start by reading the [release notes](https://github.com/immich-app/immich/releases) to figure out if I need to do something special. Usually are pure code changes, like changes internally in the server, just fine. Changes to startup scripts, dependencies, paths, environment do possible require changes to this package.

Depending on the release size I have found it useful to look at code changes as well, at least so see what files the release touches. I have written a small tool to track important files called [update.sh](https://github.com/nsg/immich-distribution/blob/master/update.sh), the output of it is included in the pull request.

This script will diff files that I like to keep track on, for example:

* Dockerfiles - I keep track on then to detect changes to dependencies, changes to startup scripts and various things that _may_ affect the snap. If the base image change, inspect if it contains any relevant changes.
* Scripts - I do not use these scripts so I need to adapt whatever they to do my startup scripts
* Env-files and docker-compose-file - Detect relevant changes, like patch or environment changes that are required
* migrations - I track database changes to see if anything relevant has changed related to [database changes](https://github.com/nsg/immich-distribution/blob/master/src/etc/modify-db.sql) that the sync feature has done.

## Test it locally

{% admonition(type="note", title="This requires snapcraft") %}
This requires that you have snapcraft installed and configured. I use LXD to build the package, but multipass should work just fine. This is not essential, if the tests pass in GitHub Actions for a simple version bump I consider that fine. For everyting else, please test it locally.
{% end %}

### Build and install

#### Use "snap try"

I usually run `make try`, that will build and install the snap.

{% admonition(type="info", title="About snap try") %}
In short, this will build everyting and prime it inside lxd/multipass, but instead of creating the final snap-package, it will just extract the `prime` folder. This allows you to easily inspect the files, and even modify them when troubleshooting! The prime folder will then be "installed" with the command `snap try prime`. It will behave more or less like a normal snap package.

This is really convenient, but please note that snapd can be a little confused in a few corner cases. To fully nuke the state and start over with a clean slate, use `make reset try`.
{% end %}

#### Use "snap install"

If you like to build an actual snap file and install it, run `make`.

{% admonition(type="info", title="About snap install") %}
This builds and installs the unsigned snap package. This is equalant to the real releases, but it slower and less convenient compared to the snap try option.
{% end %}

#### Use "snapcraft"

You can of course also use `snapcraft` directly like any other snap package if you prefer, and them manually install it.

{% admonition(type="info", title="About snapcraft") %}
Use this if you prefer control, like if you like to rebuild a specific part or stage.
{% end %}

### Run tests

#### Selenium

To run the tests, you need to start the selenium container. Currently it assumes that you run podman but feel free to contribute alternatives. Start it with `make selenium`.

Run the tests with a `make tests`, will download a few test files and run them agains you newly installed instance on localhost. These tests requires that the instance if freshly installed. A user called `foo@example.com` with the password `secret` will be created.

#### Manual

{% admonition(type="warning", title="Selenium") %}
If you have executed the above selenium tests, you should have a user called `foo@example.com` with the password `secret`. Log in with that!
{% end %}

The selenium tests covers the most common use cases, so I usually only do manual tests to make sure that everyting "looks good", and to troubleshoot problems.

To inspect all the logs, run the following command to tail all services:

```
journalctl -fu snap.immich-distribution.*
```

Note that the package need to be installed for the `*` to expand properly.

## Merge the Pull Request

When the PR is merged, a Github Action will build the snap that will end up in the store. It will be automatically signed and published to the edge channel.

## Release to beta

I release the revision in the `edge` channel to `beta`. I ask the beta testers to test the beta release and inspect the logs closely and make sure that the everyting works.

{% admonition(type="note", title="Beta testers") %}
It's rare that I beta test a release, in most cases I will immediately release it to candidate.
{% end %}

## Relese to candidate

If everyting looks fine, I will release it to `candidate`. My production deployment uses this channel. I will live with this release to make sure that everyting works.

## Release to stable

If everyting works for me, with no known problems, I will release this to the `stable` channel. I usually release this 2-3 days after candidate, but it may be faster if the mobile client is broken (that's unusual).

## The tracking issue

Keep it open for a few days for users to see, read and possible comment.

{% admonition(type="note", title="Repeat") %}
It's not uncommon that Immich has released a new release at this point :man_facepalming: so let's start over!
{% end %}
