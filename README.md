# Immich Distribution

> First an important mention, this is **NOT** an official package of [Immich](https://immich.app/). If you like to have Immich installed directly from the Immich project use the official [Docker images](https://immich.app/docs/install/docker-compose). Do not report bugs to upstream _unless_ you are sure that the same bug is present in the upstream images.

<p align="center">
  <img src="docs/immich-dist.png">
</p>

## About this distribution

This is an [Immich](https://immich.app/) Distribution packaged inside a [snap](https://snapcraft.io/docs) package. I have used the excellent [Nextcloud snap](https://github.com/nextcloud-snap/nextcloud-snap/) as an inspiration for this. The package is inspired of the official Immich images. It will be similar, but not identical with the official Docker-based installation. It will ship the same software, but with limited customability. Extra tools are included, they should be non-intrusive and you can ignore them if you prefer.

## Requirements

Immich [recommends](https://immich.app/docs/install/requirements) at least 2GB RAM (4 preferred) with 2 CPU cores (4 preferred). [Snapd requires](https://snapcraft.io/docs/installing-snapd) that you use Linux, Ubuntu is has it re-installed and is recommended. Only 64-bit x86 CPU:s are supported (amd64), ARM builds are possible but I do not build these packages because I have no ARM-based system with enough resources to test it. Finally you probably need a lot of free disk space, images are stored at `/var/snap`.

## Installation

```sh
snap install <package name> # sample, not yet published to the store
```

When it's published to the [Snap Store](https://snapcraft.io/store) it's just a simple command away (sample above). The package is about 400MB in size so it can take a little while to install. Point your browser to port 80 to get started!

### Security

Immich processes are exposed on localhost. Dedicate a server, VM or container for Immich exclusively. I run this snap inside an [LXD container](https://linuxcontainers.org/lxd/introduction/) for better isolation.

### Updates

Updates are automatic, this is a core concept of Snap. If you do not like this, stay away! If you prefer an easy to maintain and automatic installation that "just works", carry on reading! **Do not expect me to release updates the same day** as an upstream Immich release. I hope to do so in a **reasonable time**. When Immich releases an update I will build and push an update to the candidate channel (my server uses this channel) and try it out for a few days. I will relese the build to the stable channel after a few days, if everyting works.

### Channels

| Channel | Used for |
| ------- | -------- |
| stable  | The default channel, stable release, **use this** |
| candidate | I beleve this is stable, but it's released for testing for a few days |
| beta | Help me to try out new code |
| edge | Development release, will break from time to time |

Automatic updates from "candidate to candidate", "stable to stable" or "stable to candidate" should always work. Otherwise I consider it a bug. The snap may contain migration logic that makes hard to downgrade, this is not supported.

## Included software

| Software | Note |
| -------- | -------- |
| Immich Server | This is the server component of Immich that provides Immich API |
| Immich Microservices | This service provides background processing of assets for Immich Server |
| Immich Machine Learning | Object detection and image classifier, provides and API for Immich |
| Immich Web | The Immich web pages |
| Postgres | Relational database used by Immich |
| Redis | Fast key-value database used by Immich |
| HAProxy | Service that proxies traffic to Immich web and server |
