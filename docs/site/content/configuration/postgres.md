+++
title = "Postgres"
+++

# Postgres

Immich uses [PostgreSQL](https://www.postgresql.org) as a database, the database is included in this package. It can be useful to access the database, so I have added and exposed the `psql` utility. You can access the database like this:

{% code(title="Access Immich Database") %}
```bash
sudo immich-distribution.psql -d immich
```
{% end %}

To connect with an external tool, fetch the database password with `sudo snap get immich-distribution database-password` and connect normally.

{% code(title="Use external command with password") %}
```bash
psql -h 127.0.0.1 -U postgres -d immich
```
{% end %}
