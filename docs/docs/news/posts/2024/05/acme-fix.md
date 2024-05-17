---
date: 2024-05-16 10:00:00
authors: [nsg]
---

# ACME port conflict

I noticed from the logs of the ACME client (lego) that there was a port conflict preventing new certificates from being issued. I uses port `8081` since last year. About two months ago Immich started to use the same port to expose metrics.

To resolve the port conflict preventing new certificates from being issued, I decided to change the port used by the ACME client (lego). While the ACME thing is something internal that users do not need to worry about, the Immich metrics ports could be utilized by my users. Therefore, I made the decision to switch the Lego port instead of the Immich port.

## The problem with new ports

Initially I just [changed the Lego port to `8181`](https://github.com/nsg/immich-distribution/commit/aa2793164347a2f1c092ffd36485e2d00704216b) and [explicitly configured Immich to use `8081`](https://github.com/nsg/immich-distribution/commit/519bc64716bc90d4808be3bec91a43d43391ba97). The problem with new ports and an automatically updating application is that I have no idea if a user have additional software already installed utilizing `8181`. I thought about picking a higher port, reducing the risk of a port conflict to almost 0 but I choose a more programmatic approach.

## Dynamic port assignment

Last year [I introduced](https://github.com/nsg/immich-distribution/pull/118) two new configuration options that [allowed the user to change](../../../../configuration/haproxy.md) the HTTP (default `80`) and HTTPS (default `443`) ports. I already had the code for most of the logic, so I wrote a simple function to detect a free port in the `34000-36000` port range and used that port by default.

```sh
sudo snap get immich-distribution acme-port
34000
```

On my system I got port `34000` and most likely, so did you. to change the port use this command:

```sh
sudo snap set immich-distribution acme-port=1234
```

## The future

I plan to utilize this new functionality to assign internal ports for Immich (`3001-3003`), as well as the database ports `5432` (postgres) and `6379` (redis). My goal is to make the installation of Immich Distributions easier on systems that have other services running.
