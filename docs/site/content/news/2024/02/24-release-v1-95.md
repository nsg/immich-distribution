+++
template = "blog-post.html"
title = "Release v1.95"
date = "2024-02-24"
path = "news/2024/02/24/release-v195"
authors = ["nsg"]
+++


This release bumps the version of [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) to 0.2.0. The index format has changed and a few database operations are needed. Immich runs these operations as part of it's normal migrations. The problem is that Postgres needs to be restarted **after**. So the official instructions are just that. "Upgrade, wait, restart".

## Story time!

I considered to manually run these database migrations as part of the update hook, alternatively as part of the database startup script. That would have been a clean solution, but I'm a little worried that I would have missed something extra that Immich needes, so I followed the official instructions.

The database restart needs to occur _after_ immich has started. I considered writing some form of logic to detect the appropriate time, but to keep things simple, I just wait five minutes. A simple solution, good enough!

I created a simple "migration" service that I use to trigger this logic. It felt better to write something more generic instead of a one off script that I needed to keep around for months (a few users are slow to upgrade).

## What to expect

Zero care automatic updates as usual. If you actively use the system the first five minutes you may notice that search is broken. It should fix it self **after five minutes**.

## Troubleshoot

If search is still broken, please [open an issue](https://github.com/nsg/immich-distribution/issues) and report the output of:

{% code(title="Inspect the new migration tools migration version") %}
```bash
sudo snap get immich-distribution manager-migrations-version
```
{% end %}

{% code(title="Inspect the manager service") %}
```bash
systemctl status snap.immich-distribution.manager.service
```
{% end %}
