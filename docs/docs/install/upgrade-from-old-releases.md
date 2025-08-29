# Upgrade from old releases

Upgrading after skipping many revisions can be risky. Database migrations and other code are written and tested sequentially. Skipping many can surface untested combinations.

## Find your current revision

To see what revision (rev) you have installed, run the following command:
```bash
snap list immich-distribution
```

Example below (with real data from the stable channel)
```
Name                 Version   Rev  Tracking       Publisher  Notes
immich-distribution  {{snapstore_version}}  {{snapstore_revision}}  latest/stable  nsg        -
```

## How to upgrade

Assuming that run the stable channel (you should), the latest revision is `{{snapstore_revision}}`. Any update before `{{snapstore_revision_block}}` is blocked. This should only happen if you have manually disabled automatic updates, if this is the case please read the [news](/news) carefully.

You need to upgrade to an intimidate version, for example if your current version is `{{snapstore_revision_old}}`, you need to upgrade to `{{snapstore_revision_oldish}}`, then `{{snapstore_revision_newish}}` and finally `{{snapstore_revision}}` (less than five revisions each time).

```sh
sudo snap refresh immich-distribution --revision=1234
```

!!! danger
    If you try to upgrade directly from revision **{{snapstore_revision_block}}** or older to **{{snapstore_revision}}**, updates will be blocked.

!!! note
    The block functionality was implemented in revision **227**, but everything else here is still true. If you have disabled automatic updates, please do not upgrade to many revisions at once.
