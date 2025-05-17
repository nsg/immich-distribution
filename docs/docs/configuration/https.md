# Configure HTTPS

This page explains how to enable the built-in HTTPS certificate management in Immich Distribution. If you already have an existing infrastructure for TLS certificates (e.g., a reverse proxy like Nginx or Caddy), you can ignore this section and configure your load balancer to forward traffic to Immich Distribution on port 80.

## Prerequisites

HTTPS requires a domain name (e.g., `immich.example.com`); it will not work with IP addresses (e.g., `192.168.1.10`). Immich Distribution has built-in support for issuing free TLS certificates from [Let's Encrypt](https://letsencrypt.org/).

You can use a domain name you already own, purchase one, or use a free dynamic DNS provider. Point the DNS A record for your chosen domain name to your Immich server's public IP address. Ensure you can access your Immich instance via `http://your.domain.name` (note the **http**).

Your Immich installation must be accessible from the internet on TCP port 80. If you are running this on a home network, you will need to configure port forwarding on your router to forward external port 80 to your Immich server's internal port 80. A server hosted with a cloud provider typically won't require router port forwarding, but you may need to adjust firewall rules.

## Configure

Use snapd's configuration options to set `acme-domain` and `acme-email` to their appropriate values. The domain name should be the one pointing to your Immich installation. Please use a real email address, as it will be associated with your Let's Encrypt account. Let's Encrypt uses this email to send important notifications about your certificate, such as expiration warnings.

```sh 
sudo snap set immich-distribution acme-domain="your.domain.name"
sudo snap set immich-distribution acme-email="immich@example.com"
```

## Issue the certificate

The following command will attempt to register a Let's Encrypt account (if one doesn't exist for the email) and issue the certificate. It will also automatically enable HTTPS in Immich Distribution using this new certificate.

```sh
sudo immich-distribution.lets-encrypt
```

Try accessing your site via `https://your.domain.name`. If it loads successfully, you are all set! The certificate should renew automatically before it expires.

## Troubleshoot

1. Ensure your Immich instance is accessible on port 80 from the public internet.
2. Requests to `http://your.domain.name/.well-known/acme-challenge/` must reach the Immich Distribution instance for the ACME challenge to succeed.
3. Check the HAProxy logs for errors: `journalctl -eu snap.immich-distribution.haproxy`.
4. You can re-run `sudo immich-distribution.lets-encrypt`. However, be aware of Let's Encrypt's rate limits if you run it too frequently.
5. For extended troubleshooting without hitting production rate limits, consider using the [Let's Encrypt staging environment](https://letsencrypt.org/docs/staging-environment/) by setting `sudo snap set immich-distribution acme-staging="true"` before running the command.

## Disable HTTPS

```sh
sudo snap set immich-distribution https-enabled="false"
```
