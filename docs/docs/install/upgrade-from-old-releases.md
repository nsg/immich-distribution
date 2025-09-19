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

!!! warning "Temporary workaround"
    Please note, if you are stuck at `v1.138.1` (revision `227`), this is due a bug on my part I will push out a fix in the next days that should solve it. I need to rework this logic a little and I plan to do so over the weekend.

    If you can't wait it's safe to do the following:

    ```bash
    touch /var/snap/immich-distribution/common/no-post-refresh-hook
    snap refresh immich-distribution
    rm /var/snap/immich-distribution/common/no-post-refresh-hook
    ```

    Disabling the post-refresh hook is safe between version v1.138 to v1.141. If you have executed commands below and are stuck at a later revision, this should still work, but you may end up in a non stable channel. If you need help, open an issue at GitHub and I will help you. I will try to update this later with instructions how to return to the stable channel.

Assuming that run the stable channel (you should), the latest revision is `{{snapstore_revision}}`. Any update before `{{snapstore_revision_block}}` is blocked. This should only happen if you have manually disabled automatic updates, if this is the case please read the [news](/news) carefully.

You need to upgrade to an intimidate version, for example if your current version is `{{snapstore_revision_old}}`, you need to upgrade to `{{snapstore_revision_oldish}}`, then `{{snapstore_revision_newish}}` and finally `{{snapstore_revision}}` (less than 3 revisions each time).

```sh
sudo snap refresh immich-distribution --revision=1234
```

!!! danger
    If you try to upgrade directly from a revision before **{{snapstore_revision_block}}** to **{{snapstore_revision}}**, updates will be blocked.

!!! note
    The block functionality was implemented in revision **228**, but everything else here is still true. If you have disabled automatic updates, please do not upgrade to many revisions at once.
