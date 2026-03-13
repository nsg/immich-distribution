<div align="center">
  <img src="docs/site/static/assets/immich-dist.png" alt="Immich Distribution" width="200">
  <h1>Immich Distribution</h1>
  <p>A self-contained <a href="https://snapcraft.io/docs">snap package</a> for <a href="https://immich.app/">Immich</a> — self-hosted photo and video management.</p>

  [![immich-distribution](https://snapcraft.io/immich-distribution/badge.svg)](https://snapcraft.io/immich-distribution)
</div>

---

## About

Immich Distribution is an independent community project that packages [Immich](https://immich.app/) as a [snap](https://snapcraft.io/docs). It bundles the Immich server, machine learning, a database, and supporting services into a single installable package with automatic updates. Extra tools for backup, restore, file sync, and HTTPS are included but optional.

This project is not affiliated with the upstream [Immich project](https://immich.app/), its developers, or [FUTO](https://futo.org). If you prefer the official Docker-based installation, see the [upstream docs](https://immich.app/docs/install/docker-compose). Please only report bugs upstream if they also occur in the official images.

## Quick Start

```
sudo snap install immich-distribution
```

Open `http://<your-server-ip>` in your browser to complete setup. For detailed installation instructions, including hardware requirements and configuration, see the [installation guide](https://immich-distribution.nsg.cc/install/).

## Included Software

| Component | Description |
| --------- | ----------- |
| Immich Server | API, microservices, and web interface |
| Immich Machine Learning | Object detection and image classification |
| [PostgreSQL](https://www.postgresql.org/) | Relational database |
| [Redis](https://redis.io/) | Key-value store for caching and job queues |
| [HAProxy](https://www.haproxy.org/) | Reverse proxy for HTTP/HTTPS traffic |
| [lego](https://github.com/go-acme/lego) | Let's Encrypt ACME client for TLS certificates |
| [Sync Service](https://immich-distribution.nsg.cc/configuration/sync/) | Two-way folder synchronization with Immich |
| [Backup & Restore](https://immich-distribution.nsg.cc/configuration/backup-restore/) | Database and asset backup tools |

## Configuration

Configure the snap with `snap set` and `snap get`:

```bash
# Enable HTTPS with Let's Encrypt
sudo snap set immich-distribution acme-domain=photos.example.com acme-email=you@example.com

# Enable daily database backups
sudo snap set immich-distribution backup-database-daily=true
```

See the [configuration documentation](https://immich-distribution.nsg.cc/configuration/) for all available options.

## CLI Tools

All commands are available as `immich-distribution.<command>`:

| Command | Description |
| ------- | ----------- |
| `immich-admin` | Immich server administration CLI |
| `backup` | Back up database and/or assets |
| `restore` | Restore from a backup |
| `psql` | PostgreSQL client |
| `lets-encrypt` | Initialize Let's Encrypt certificate setup |

See the [CLI documentation](https://immich-distribution.nsg.cc/configuration/cli-administration/) for full usage details.

## Documentation

Full documentation at [immich-distribution.nsg.cc](https://immich-distribution.nsg.cc).

## License

All files in this repository are released under the [MIT](https://opensource.org/license/mit) license. Upstream Immich was also licensed under MIT but changed to [AGPLv3](https://opensource.org/license/agpl-v3) after [2024-02-12](https://github.com/immich-app/immich/pull/7046).
