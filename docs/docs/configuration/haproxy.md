# HAProxy

You can inspect the HAProxy statistics and status page by navigating to `/haproxy` on your Immich instance (e.g., `http://your.domain.name/haproxy`). This page can be useful for troubleshooting or getting an overview of the installation's operational status. The HAProxy configuration file used by Immich Distribution can be [inspected here](https://github.com/nsg/immich-distribution/blob/master/src/etc/haproxy.cfg).

## Enable https frontend

```bash title="Enable https frontend"
sudo snap set immich-distribution https-enabled="true"
```

The command above enables the TLS frontend in HAProxy. This is automatically enabled if you configure [HTTPS with Let's Encrypt](/configuration/https).

## Disable HTTP

```bash title="Disable HTTP frontend"
sudo snap set immich-distribution http-enabled="false"
```

The command above disables the HTTP frontend in HAProxy, forcing all traffic to use HTTPS. **Important:** You must first enable and verify that HTTPS is working properly before disabling HTTP. The HTTP frontend is required for the initial Let's Encrypt certificate acquisition process (HTTP-01 challenge). Only disable HTTP after you have successfully obtained your certificates and confirmed that HTTPS access is functioning correctly.

## Change port numbers

By default, HAProxy listens on `*:80` (all network interfaces, TCP port 80) for HTTP traffic, and `*:443` for HTTPS traffic if enabled. If you need to change these default ports (e.g., if they are already in use by another service), you can update the following configuration keys:

```bash title="Use port 8880 for HTTP traffic"
sudo snap set immich-distribution haproxy-http-bind="*:8880"
```

```bash title="Use port 4443 for HTTPS traffic"
sudo snap set immich-distribution haproxy-https-bind="*:4443"
```

## Loading screen

The loading screen shown when Immich services are starting or down uses HAProxy statistics to display its information.
![](/assets/immich-loading.png)
