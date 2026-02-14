+++
title = "Upgrade from old releases"
+++

# Upgrade from old releases

Upgrading after skipping many revisions can be risky. Database migrations and other code are written and tested sequentially. To make this safer, upgrades are grouped into "eras" that must be applied in order.

## How to upgrade

Systems that are regularly updated should move between supported eras sequentially (for example: 1 → 2 → 3 → 4). If automatic updates have been disabled or you’ve fallen far behind and attempt to jump across eras (for example: 1 → 3), the post-refresh hook will block the upgrade to protect your data. In that case, refresh to an intermediate release from the next era, apply it, and then continue to the latest. See the [news](/news) for any additional notes.

## Historic Eras (stable channel)

| Era | Version  | Revision | Notes                 |
| --- | ---------| ---------| --------------------- |
| 2   | v2.5.0   | -        | pgvecto.rs removed from image, [VectorChord migration](/news/2025/08/31/vectorchord-migration-rollout/) completed |
| 1   | v1.142.1 | 240      | Eras implemented, [VectorChord migration](/news/2025/08/31/vectorchord-migration-rollout/) in progress |
| 0   | -        | -        | A release before revision 240 is counted as era `0` |

To move to a specific era on the stable channel, refresh to the revision listed for that era:

```sh
sudo snap refresh immich-distribution --revision=<REVISION>
```

## Find your current revision

To see what revision (rev) you have installed, run the following command:
```bash
snap list immich-distribution
```

Example below (with real data from the stable channel)
```
Name                 Version   Rev  Tracking       Publisher  Notes
immich-distribution  {{ snapstore_version() }}  {{ snapstore_revision() }}  latest/stable  nsg        -
```

## A note about Eras

Eras are a safety feature in Immich Distribution. They prevent skipping too many versions at once, which could otherwise leave your system in an unsupported state or corrupt your database. Upstream Immich does not support large upgrade jumps; eras help protect your data by requiring sequential era-by-era upgrades. Most users who keep their systems up to date will never notice or need to care about eras.

