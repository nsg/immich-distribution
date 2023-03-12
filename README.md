# Immich Distribution

> First an important mention, this is **NOT** an official package of [Immich](https://immich.app/). If you like to have Immich installed directly from the Immich project use the official [Docker images](https://immich.app/docs/install/docker-compose). Do not report bugs to upstream _unless_ you are sure that the same bug is present in the upstream images.

<p align="center">
  <img src="docs/immich-dist.png">
</p>

## About this distribution

This is an [Immich](https://immich.app/) Distribution packaged inside a [snap](https://snapcraft.io/docs). I have used the excellent [Nextcloud snap](https://github.com/nextcloud-snap/nextcloud-snap/) as an inspiration for this. This is still a work in progress and it's possible that I never finish this project.

## Design

This package will keep to the spirit of Immich, but I will similar but not identical with the official Docker Compose-based installation.

## Postgres

* Postgres only allows authorized connections over TCP.
* To access the database without a password use `sudo immich-distribution.psql`.
* Execute `sudo snap get immich-distribution database-password` to see the password, user is `postgres`.
* Immich uses a database called `immich`.

## Redis

* Allows unauthorized connections
* Only listens (and allows) connections from localhost

## Immich Services

The services are running at port 3000 (web), 3001 (server), 3002 (microservices) and 3003 (machine learning). The snap do not provide a network namespace (like Docker) so another process/user on the same system could access these ports directly.

## HAProxy

I use [HAProxy](https://www.haproxy.org) to proxy the traffic to Immich Server and Immich Web. HAProxy Stats is enabled on [127.0.0.1:8080](http://127.0.0.1:8080).
