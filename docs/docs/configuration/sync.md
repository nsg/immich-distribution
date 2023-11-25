# Sync Feature

!!! Note
    This page describes the custom sync feature, and not any built in Immich sync functionality like Immich CLI/import. I maintain this feature because it fits my workflow better compared to the built in options that Immich offers. I will support and use this myself until Immich implements something similar, or it breaks in an unfixable manner.

Immich is a fantastic application and when I started to use it earlier this year I investigated if it was possible for me to "hack in" a few missing features while I wait for official support, or maintain my hacks indefinitely if they are never implemented. One of these features where image synchronization and this "sync feature" was born.

## Functionality

Almost fully two-way synchronization between your phone and Immich. Add or remove an image on your phone and the changes are synced back to Immich. Deleted images inside Immich Web also synchronizes back to your phone, making it easy to clean up back pictures in the comfort of the much larger screen on your computer.

``` mermaid
graph LR
P("📱 Phone")
S("🌹 Immich")
CLI{{"Immich API Upload Image"}}
API{{"Immich API Delete Image"}}

P -- "🌄 New picture" ---> CLI --> S
P -- "⛔ Deleted picture" ---> API --> S
S -- "⛔ Deleted picture" ---> P
```

This gives me the freedom to use any application of my choice, on my phone and computer.

!!! Note "I can for example"
    Start to delete all these bad pictures from my vacation in my phones default gallery application. Open the laptop when I get home and carry on in Immich Web. Realize that this would be easier to do from a classic file manager, open the sync-folder on my laptop and delete the rest.

    Overall you are free to use whatever application and tool that you prefer to clean up and organize. You are not restricted to only use Immich Web and Mobile.

## Prerequisites

### File synchronization software

Any file synchronization software of your choice, for full functionality if need to sync in booth directions, both additions and deletions. I have picked [Syncthing](https://syncthing.net) for this, it works well both on my computers, servers and Android Phone. The software need to sync files to `/var/snap/immich-distribution/common/sync/<user uuid>/<any folder>`

### File permissions

You need to make sure that Immich Distribution Sync has permissions to read **and** remove files added by the sync solution.

## Configure

The sync functionality can be enabled with the following command.

```bash
snap set immich-distribution sync-enabled=true # (1)
```

1. or `false` to disable the service

The sync service uses an API Key so you need to generate one in Immich Web. API Keys can be generated under your users account settings. Configure your API Key like this:

```bash
snap set immich-distribution sync="lECqjpwl4KdlfI7z8jOJoWXjbtaxGp5HLzJ9zU8Wnc"
```

!!! Note "Multiple users"
    To configure multiple sync services for several users, specify both keys separarated by a space.

Inspect the sync service logs with:

```bash
journalctl -eu snap.immich-distribution.sync-*
```

## My Setup

This is a more detailed schema of _my_ setup, feel free to configure and use whatever software that you like. I have configured [Syncthing](https://syncthing.net) to synchronize my phones camera roll/folder with `/var/snap/immich-distribution/common/sync/b85e...6a4b/phone`.

``` mermaid
graph TB
P("📱 Phone (Camera)")
IS("🌹 Immich Server")
IW("🌹 Immich Web")
SY("/var/snap/.../sync/UUID/phone")
CLI{{"Immich API Upload Image"}}
API{{"Immich API Delete Image"}}
SYNC{{"Sync Service"}}

P -- "Syncthing Sync" --- SY

SY -- "🌄 New picture" ---> SYNC
SY -- "⛔ Deleted picture" ---> SYNC
SYNC -- "⛔ Deleted picture" ---> SY

SYNC -- "🌄 New picture" ---> CLI --> IS
SYNC -- "⛔ Deleted picture" ---> API --> IS
IS -- "⛔ Deleted picture" ---> SYNC
IS -- "🌄 New picture" ---> IW
IW -- "⛔ Deleted picture" ---> IS
```
