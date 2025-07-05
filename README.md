# Immich Distribution

Immich Distribution is an independent community project that packages the software in a snap package. This project is not affiliated with the upstream [Immich project](https://immich.app/), its developers, or [FUTO](https://futo.org). For more information, refer to the [documentation site](https://immich-distribution.nsg.cc).

- If you'd like to install Immich directly from the upstream project, use the official [Docker images](https://immich.app/docs/install/docker-compose).
- Please only report bugs upstream if they also occur in the official images.

<p align="center">
  <img src="docs/docs/assets/immich-dist.png">
</p>

## About

In short, this is an [Immich](https://immich.app/) Distribution packaged inside a [snap](https://snapcraft.io/docs) package. The package is inspired by the official Immich images. It will be similar, but not identical with the official Docker-based installation. Extra tools are included; they are non-intrusive and can be ignored if you prefer.

<strong>For more information see the project page at https://immich-distribution.nsg.cc</strong>

<p align="center">
  <a href="https://immich-distribution.nsg.cc"><img src="docs/docs/assets/button.png"></a>
</p>

## Installation
[![immich-distribution](https://snapcraft.io/immich-distribution/badge.svg)](https://snapcraft.io/immich-distribution)

```
sudo snap install immich-distribution
```

For detailed installation instructions, including hardware requirements, automatic updates, and configuration—see the [installation documentation](https://immich-distribution.nsg.cc/install/) on the project’s website. 

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

## CLI Extensions

Immich Distribution extends the upstream Immich CLI with additional commands for automation and administration. These commands are fully non-interactive and suitable for scripting and unattended use.

### Create Admin API Key

Generate API keys for the admin user directly from the command line:

```bash
# Create an API key with all permissions (simplest approach)
sudo immich-distribution.immich-admin create-admin-api-key

# Create an API key with a custom name
sudo immich-distribution.immich-admin create-admin-api-key --name "My Admin Key"

# Create an API key with specific permissions (e.g., for sync service)
sudo immich-distribution.immich-admin create-admin-api-key \
  --name "Sync Service Key" \
  --permissions "asset.upload,asset.delete,user.read"
```

**Options:**
- `--name, -n`: Set a custom name for the API key (default: "Admin CLI Key")
- `--permissions, -p`: Specify permissions as a comma-separated list, or use "all" for full access (default: "all")

This command is particularly useful for:
- Initial setup and configuration automation
- Creating API keys for the [sync service](https://immich-distribution.nsg.cc/configuration/sync/)
- Scripted deployments and CI/CD pipelines
- Headless server management

## License

All files in this repository are released under the [MIT](https://opensource.org/license/mit) license. Upstream Immich was also licensed under the MIT license, but have changed to [AGPLv3](https://opensource.org/license/agpl-v3) after [2024-02-12](https://github.com/immich-app/immich/pull/7046).
