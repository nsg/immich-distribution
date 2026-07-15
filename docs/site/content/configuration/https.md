+++
title = "HTTPS"
+++

# HTTPS

Immich Distribution can serve traffic over HTTPS, either with the built-in Let's Encrypt (ACME) certificate management or with certificates you provide yourself. This page lists the related configuration options, commands and file locations. For step-by-step setup instructions, see the [Configure HTTPS guide](@/guides/https.md).

## Configuration options

Options are set with `sudo snap set immich-distribution <option>="<value>"` and inspected with `snap get`.

| Option | Default | Description |
| ------ | ------- | ----------- |
| `acme-domain` | *(unset)* | Domain name to issue a Let's Encrypt certificate for. When unset, manually placed certificates are used instead. |
| `acme-email` | *(unset)* | Email address associated with your Let's Encrypt account. Used for important notifications, such as expiration warnings. |
| `acme-challenge-type` | `http` | ACME challenge type: `http` (HTTP-01, requires port 80) or `tls` (TLS-ALPN-01, requires port 443). |
| `acme-staging` | *(unset)* | Set to `true` to use the [Let's Encrypt staging environment](https://letsencrypt.org/docs/staging-environment/) for testing without hitting production rate limits. |
| `acme-port` | *(automatic)* | Internal port used by the ACME client, allocated automatically from the `34000-36000` range. You normally never need to touch this. |
| `https-enabled` | `false` | Enables the HTTPS frontend in HAProxy. Set automatically when `immich-distribution.lets-encrypt` succeeds; set it manually when using your own certificates. |

## Commands

```sh
sudo immich-distribution.lets-encrypt
```

Registers a Let's Encrypt account (if one doesn't exist for `acme-email`), issues a certificate for `acme-domain` and enables HTTPS. Renewals happen automatically before the certificate expires.

## File locations

Manually managed certificates are placed in the HAProxy certificate directory:

| File | Content |
| ---- | ------- |
| `/var/snap/immich-distribution/common/acme/haproxy/cert.crt` | Certificate |
| `/var/snap/immich-distribution/common/acme/haproxy/cert.crt.key` | Private key |

The files should be owned by `root:root` with mode `600`. Restart HAProxy after replacing them: `sudo snap restart immich-distribution.haproxy`.

## Related options

The HTTP and HTTPS frontends and their ports are managed by HAProxy. See the [HAProxy](@/configuration/haproxy.md) page for `http-enabled`, `haproxy-http-bind` and `haproxy-https-bind`.
