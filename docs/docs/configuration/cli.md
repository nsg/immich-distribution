# Immich CLI

The Immich CLI is a [command](https://github.com/immich-app/CLI) that's included in the snap package. It used to import assets in to an Immich installation. Read the [upstream documentation](https://immich.app/docs/features/bulk-upload) for more information.

```bash title="List the CLI:s help page"
immich-distribution.cli -h
```
!!! Warning "A note about permissions"

    The snap is contained in a sandbox so it is restricted from where is can read. By default it can read from `$HOME/snap/immich-distribution/current` and `.../common` and from the system global locations at `/var/snap/immich-distribution/current` and `.../common`.

    This can be limiting so consider to install Immich CLI manually outside the snap if your usecase require it.

## For example

```bash title="Upload files to Immich"
immich-distribution.cli upload --key "mySecrEtKey" --recursive ~/snap/immich-distribution/current/
```
