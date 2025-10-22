+++
title = "Sync Feature"
+++

# Sync Feature

{% admonition(type="note") %}
This page describes a custom sync feature, distinct from Immich's built-in sync functionalities like the Immich CLI or import tool. I maintain this feature because it better suits my workflow compared to the built-in options Immich offers. I will continue to support and use this feature myself until Immich implements a similar solution, or if it becomes unfixably broken.
{% end %}

Immich is a fantastic application. When I started to use it, I investigated if it was possible for me to "hack in" a few missing features while waiting for official support, or maintain my hacks indefinitely if they are never implemented. One of these was image synchronization, which led to the creation of this "sync feature".

## Functionality

Provides nearly complete two-way synchronization between your phone and Immich. Adding or removing an image on your phone syncs the changes to Immich. Deletions within Immich Web also synchronize back to your phone, making it easy to manage pictures on your computer's larger screen.

``` mermaid
graph LR
P("📱 Phone")
S("🌹 Immich")
CLI{{"Immich API Upload Image"}}
API{{"Immich API Trash Image"}}

P -- "🌄 New picture" ---> CLI --> S
P -- "⛔ Deleted picture" ---> API --> S
S -- "⛔ Deleted picture" ---> P
```

This offers the flexibility to use any application of your choice on your phone and computer.

{% admonition(type="note", title="I can for example") %}
For example, you can start deleting unwanted vacation pictures using your phone's default gallery app. Then, open your laptop at home and continue managing them in Immich Web. If you find it easier to use a traditional file manager, you can open the sync folder on your laptop and delete the remaining files.

Overall, you are free to use any application or tool you prefer for organizing and cleaning up your media. You are not limited to using only Immich Web and Mobile.
{% end %}

## Prerequisites

### File synchronization software

You can use any file synchronization software of your choice. For full functionality, it needs to support two-way synchronization, including both additions and deletions. I use [Syncthing](https://syncthing.net), which works well on computers, servers, and Android phones. The software needs to sync files to `/var/snap/immich-distribution/common/sync/<user_uuid>/<any_folder>`.

### File permissions

Ensure that Immich Distribution Sync has permissions to read **and** remove files managed by your chosen synchronization software.

### API key

To use the sync feature, you need an API key with appropriate permissions. The recommended approach is to create API keys through Immich Web under **Account Settings** → **API Keys**.

If you need to create API keys programmatically or via CLI, you can use the included command:

```bash
# Create API key for a specific user by email (recommended for sync)
sudo immich-distribution.immich-admin create-api-key \
  --name "Sync Service Key" \
  --permissions "asset.upload,asset.delete,user.read" \
  --user-email "user@example.com"

# Create API key for admin user with all permissions
sudo immich-distribution.immich-admin create-api-key
```

For complete documentation and all available options, see the main [README](https://github.com/nsg/immich-distribution#generate-api-keys).

## Configure

```bash
# Enable or disable the sync service
snap set immich-distribution sync-enabled=true|false

# Set one or more API keys (space-separated for multiple users)
snap set immich-distribution sync-api-key="YOUR_IMMICH_API_KEY [ANOTHER_API_KEY ...]"

# Optional: adjust delete threshold in days (default: 30)
snap set immich-distribution sync-delete-threshold=30
```

Inspect the sync service logs with:

```bash
journalctl -eu snap.immich-distribution.sync-*
```

## My Setup

Below is a detailed diagram of _my_ setup. Feel free to configure and use any software you prefer. In this example, [Syncthing](https://syncthing.net) is configured to synchronize the phone's camera roll/folder with `/var/snap/immich-distribution/common/sync/b85e...6a4b/phone`.

``` mermaid
graph TB
P("📱 Phone (Camera)")
IS("🌹 Immich Server")
IW("🌹 Immich Web")
SY("/var/snap/.../sync/UUID/phone")
CLI{{"Immich API Upload Image"}}
API{{"Immich API Trash Image"}}
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
