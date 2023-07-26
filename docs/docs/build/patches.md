# Patches

I maintains a patch for the update dialog box (Immich Web). The "New version" dialog that appears contains update instructions that do not make sense for Immich Distribution, this can confuse users. I also took the oppertunity to direct support issues to the correct place.

| Default | Patched |
| ------- | ------- |
| [![](/assets/immich-default-update-modal.png)](/assets/immich-default-update-modal.png) | [![](/assets/immich-distribution-update-modal.png)](/assets/immich-distribution-update-modal.png) |

## Generate patch

In `patches/` execute `make download-patch` to download a fresh `version-announcement-box.svelte`. I track this file to my own repo to track changes over time, so feel free to use git to see what has changed. The `update.sh` script monitors this file in the upstream repository so you should be notified if this step needs to be executed.

Update `version-announcement-box-snap.svelte` with out changes, use `version-announcement-box.svelte` as a template. Minimize the difference. When you are done, execute `make make-patch` to generate `001-version-announcement-box.patch`.
