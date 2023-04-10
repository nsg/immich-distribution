+++
title = "Install Immich Distribution"
weight = 1
+++

## Prerequisites

### snapd

A computer running Linux with [support for snapd](https://snapcraft.io/docs/installing-snapd). Most commonly used Linux distributions are supported. If you do not have any strong preferences I recommends Ubuntu, or something Ubuntu based.

### Hardware

A computer with a relatively modern Intel or AMD based CPU, for example the AVX instructionset is needed. You need **at minimum** 4GB available RAM, six or eight is preferred. You probably also need a lot of free disk space, pictures are stored at `/var/snap`.

### Type of server

A home server, or an always on computer will work just fine. If you need to access it from the outside world you could port forward port 80 (and 443 if you like to use https) from your router to Immich. An alternative is to use a VPN (like WireGuard or Tailscale) to access the server from the outside. An VPS or server running in a datacenter will of course work.

## Install

Installing Immich Distribution is easy, just execute the following command on a server. The package is over 500MB so it can take some time to install, but with a decent internet connection it should be less than a minute or two.

```sh
sudo snap install immich-distribution
```

If you installed immich-distribution to a server with the IP 192.168.1.10 open a browser and navigate to http://192.168.1.10. The stack can take up to a minute to fully start, especially the machine learning components are slow to start. You should be greeted with a screen like this indicating that Immich is still loading.

![](/img/immich-loading.png)

The page will update and reload automatically when all services are ready. This is a new install so Immich will offer you to register an admin account. The official [Post Install Steps](https://immich.app/docs/install/post-install) will guide you to get going.

If this installation is exposed to the public internet I stronly suggest that you set up https, for information how to do that see [Enable HTTPS](@/configuration/https.md)
