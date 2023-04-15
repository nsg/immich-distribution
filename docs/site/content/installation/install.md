+++
title = "Install Immich Distribution"
weight = 1
+++

## Prerequisites

### snapd

A computer running Linux with [support for snapd](https://snapcraft.io/docs/installing-snapd). Most commonly used Linux distributions are supported. If you do not have any strong preferences I recommends Ubuntu, or something Ubuntu based.

### Hardware

A computer with a relatively modern Intel or AMD based CPU, for example the AVX instructionset is needed. You need **at minimum** 4GB available RAM, six or eight is preferred. You probably also need a lot of free disk space, pictures are stored at `/var/snap`.

#### What about ARM?

There is nothing technically blocking me from adapting this package for more architectures like ARM. At the moment I do not have any ARM based systems running to test and develop ARM support, so I have focused my resources on what I use personally.

### Type of server

Any type of server/computer will work. A home server, or an always on computer will work just fine. If you need to access it from the outside world, a port forward (port 80, and 443 if you like to use https) from your router to Immich would probably work. An alternative is to use a VPN (like [WireGuard](https://www.wireguard.com/) or [Tailscale](https://tailscale.com/)) to access the server from the outside. 

A [VPS](https://en.wikipedia.org/wiki/Virtual_private_server) or server running in a datacenter will of course work. All you need to do is to install the package and you are ready to go!

### Available ports

The following ports will be used by Immich Distribution and they need to be unused.

| Port | Interface | Comment |
| ---- | --------- | ------- |
| 80   | all | HAProxy |
| 443  | all | HAProxy (only if HTTPS is enabled) |
| 3000-3003 | all | Immich |
| 5432 | lo | Postgres |
| 6379 | lo | Redis |
| 8108 | lo | Typesense |

## Install

Installing Immich Distribution is easy, just execute the following command on a server. The package is over 500MB so it can take some time to install, but with a decent internet connection it should be quite fast.

```sh
sudo snap install immich-distribution
```

### Connecting to the server

If you installed immich-distribution to a server with the IP 192.168.1.10 open a browser and navigate to http://192.168.1.10. The stack can take up to a minute to fully start, especially the machine learning components are slow to start. You should be greeted with a screen like this indicating that Immich is still loading.

![](/img/immich-loading.png)

The page will update and reload automatically when all services are ready. This is a new install so Immich will offer you to register an admin account. The official [Post Install Steps](https://immich.app/docs/install/post-install) will guide you to get going.

If this installation is exposed to the public internet I stronly suggest that you set up https, for information how to do that see [Enable HTTPS](@/configuration/https.md)
