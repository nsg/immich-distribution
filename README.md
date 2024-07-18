# Immich Distribution

Immich Distribution is an independent community project that packages the software in a snap package. This project is not affiliated with the upstream [Immich project](https://immich.app/), its developers, or [FUTO](https://futo.org). For more information, please refer to the [documentation site](https://immich-distribution.nsg.cc).

If you like to have Immich installed directly from the Immich project use the official [Docker images](https://immich.app/docs/install/docker-compose). Do not report bugs to upstream _unless_ you are sure that the same bug is present in the upstream images.

<p align="center">
  <img src="docs/docs/assets/immich-dist.png">
</p>

## About

In short, this is an [Immich](https://immich.app/) Distribution packaged inside a [snap](https://snapcraft.io/docs) package. The package is inspired of the official Immich images. It will be similar, but not identical with the official Docker-based installation. Extra tools are included, they should be non-intrusive and you can ignore them if you like.

<strong>For more information see the project page at https://immich-distribution.nsg.cc</strong>

<p align="center">
  <a href="https://immich-distribution.nsg.cc"><img src="docs/docs/assets/button.png"></a>
</p>

## Installation
[![immich-distribution](https://snapcraft.io/immich-distribution/badge.svg)](https://snapcraft.io/immich-distribution)

```
sudo snap install immich-distribution
```

For detailed installation instructions with recommendations and hardware requirements, automatic updates and configuration see the [installation documentation](https://immich-distribution.nsg.cc/install/) pages at the projects website. 

## Documentation

See the documentation site at [immich-distribution.nsg.cc](https://immich-distribution.nsg.cc) for more information.

## Included software

| Software | Note |
| -------- | -------- |
| Immich Server | This is the server component of Immich that provides Immich API, Microservices and the Website |
| Immich Machine Learning | Object detection and image classifier, provides and API for Immich |
| [Immich Distribution Sync](https://immich-distribution.nsg.cc/configuration/sync/) | Synchronize (read & write) a external folder (with a few caveats) with Immich |
| [Immich Distribution Backup](https://immich-distribution.nsg.cc/configuration/backup-restore/) | Tool for easy backup and restore of Immich |
| [Postgres](https://www.postgresql.org/) | Relational database used by Immich |
| [Redis](https://redis.io/) | Fast key-value database used by Immich |
| [HAProxy](https://www.haproxy.org/) | Service that proxies traffic to Immich web and server |
| [lego](https://github.com/go-acme/lego) | A Let's Encrypt ACME client used to checkout TLS certificates |

## License

All files in this repository are released under the [MIT](https://opensource.org/license/mit) license. Upstream Immich was also licensed under the MIT license, but have changed to [AGPLv3](https://opensource.org/license/agpl-v3) after [2024-02-12](https://github.com/immich-app/immich/pull/7046).
