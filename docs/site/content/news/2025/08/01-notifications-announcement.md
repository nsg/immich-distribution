+++
template = "blog-post.html"
title = "Important Notifications & Backup database"
date = "2025-08-01"
path = "news/2025/08/01/important-notifications--backup-database"
authors = ["nsg"]
+++


{% admonition(type="info", title="New Notification System") %}
Immich recently introduced a notification system and an API to send these notifications. I'm going to use this to inform you of important information in the future, and this is the first time you'll see a notification like this. All notifications will have a blog post like this one that contains additional information.
{% end %}

Immich has moved on from [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) to [VectorChord](https://github.com/tensorchord/VectorChord). That's a new vector extension to [Postgres](https://www.postgresql.org/) that is replacing it. At the moment Immich supports both but the old one will be deprecated in a future release.

Migration from pgvecto.rs to VectorChord should be automatic and safe, but there's always a risk. I have intentionally waited for about two months to make sure that code stabilized before pushing out this release, but to be on the safe side, I recommend highly that you make sure you have working backup.

There are two backup systems in Immich Distribution. The one [provided by us](/configuration/backup-restore/) and the one [provided by the upstream Immich project](https://immich.app/docs/administration/backup-and-restore). Please enable at least one of these backup options so it's possible to restore your installation if anything breaks.

You will find backups for Immich Distribution in `/var/snap/immich-distribution/common/backups/` and you will find backups made by the builtin feature in Immich in `/var/snap/immich-distribution/common/upload/backups/`. You can also run the following command to list all backups: `immich-distribution.backup -l`.

As usual, I will always test everything to make sure this is a smooth, automatic zero care upgrade.
