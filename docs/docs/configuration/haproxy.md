# HAProxy

You can inspect the HAProxy stats status page at `/haproxy`. It can be useful to troubleshoot or just to get a feeling about the installations status. You can [inspect the configuration here](https://github.com/nsg/immich-distribution/blob/master/src/etc/haproxy.cfg).

## Enable https frontend

```bash title="Enable https frontend"
sudo snap set immich-distribution https-enabled="true"
```

The above command will enable the TLS frontend, this will be enabled if you configure [https](/configuration/https) with Let's encrypt.

## Loading screen

The loading screen below uses haproxy stats to display it's information. The loading screen is displayed if the Immich Web frontend is down.

![](/assets/immich-loading.png)
