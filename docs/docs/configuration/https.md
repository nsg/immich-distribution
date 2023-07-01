# Configure HTTPS

This page will show you how to enable the built in HTTPS certificate managent in Immich Distribution. If you already have infrastructure for TLS certificates feel free to ignore this sections and point your load balancer to port 80.

## Prerequisites

HTTPS requires a domain name (like `immich.example.com`), it will not work with IP-numbers (like 192.168.1.10). Immich Distribution has built in support to issue free certificates from a service called [Let's Encrypt](https://letsencrypt.org/).

Either use a domain name you already own, buy one or use a free provider. Point the DNS name to your Immich server and make sure that you can access it via http://my.domain.name (note **http**).

Your Immich installation need to be accessable on port 80 over the internet. If you run this at your home you need to port forward port 80 from your router. A public server, like a server at a cloud provider would not have this problem (ignoring possible firewall rules).

## Configure

Use snapd:s configuration options to set `acme-domain` and `acme-email` to appropriate values. The domain name should be the one pointing to your Immich installation, and please use a real email address, it's used for your Let's Encrypt account. Let's Encrypt uses it to send important information about your certificate.

```sh 
sudo snap set immich-distribution acme-domain="my.domain.name"
sudo snap set immich-distribution acme-email="immich@example.com"
```

## Issue the certificate

The following command will register an Let's Encrypt account, and issue the certificate. It will also enable HTTPS in Immich using your brand new certificate.

```sh
sudo immich-distribution.lets-encrypt
```

Try to access the site via http{==s==}://my.domain.name, if it loads you are all done! The certificate should be renewed automatically when needed.

## Troubleshoot

1. Verify that you can access Immich on port 80 over the internet.
2. `.well-known/acme` needs to be routed to Immich.
3. Check `journalctl -eu snap.immich-distribution.haproxy` for possible errors.
4. Feel free to re-run `immich-distribution.lets-encrypt`, note that you will be rate limited if you execute this _to_ many times.
5. For extended troubleshooting consider to enable the [Let's Encrypt staging environment](https://letsencrypt.org/docs/staging-environment/) with `sudo snap set immich-distribution acme-staging="true"`

## Disable HTTPS

```sh
sudo snap set immich-distribution https-enabled="false"
```
