# HAProxy

You can inspect the HAProxy stats status page at `/haproxy`. It can be useful to troubleshoot or just to get a feeling about the installations status. You can [inspect the configuration here](https://github.com/nsg/immich-distribution/blob/master/src/etc/haproxy.cfg).

## Enable https frontend

```bash title="Enable https frontend"
sudo snap set immich-distribution https-enabled="true"
```

The above command will enable the TLS frontend, this will be enabled if you configure [https](/configuration/https) with Let's encrypt.

## Change port numbers

HAProxy listens on `*:80` (all interfaces, tcp port 80) by default, and `*:443` if https is enabled. If you like to change these ports update the following configuration keys.

```bash title="Use port 8880 for HTTP traffic"
sudo snap set immich-distribution haproxy-http-bind="*:8880"
```

```bash title="Use port 4443 for HTTPS traffic"
sudo snap set immich-distribution haproxy-https-bind="*:4443"
```

## Loading screen

The loading screen below uses haproxy stats to display it's information. The loading screen is displayed if the Immich Web frontend is down.

![](/assets/immich-loading.png)
