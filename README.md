# Immich Distribution

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
* Only listen (and allows) connections from localhost
