# Configure HTTPS

This page explains how to enable HTTPS in Immich Distribution. You can use either the built-in Let's Encrypt certificate management or provide your own certificates.

If you already have an existing infrastructure for TLS certificates (e.g., a reverse proxy like Nginx or Caddy), you can ignore this section and configure your load balancer to forward traffic to Immich Distribution on port 80.

## Option 1: Automatic Let's Encrypt Certificates

### Prerequisites

HTTPS requires a domain name (e.g., `immich.example.com`); it will not work with IP addresses (e.g., `192.168.1.10`). Immich Distribution has built-in support for issuing free TLS certificates from [Let's Encrypt](https://letsencrypt.org/).

You can use a domain name you already own, purchase one, or use a free dynamic DNS provider. Point the DNS A record for your chosen domain name to your Immich server's public IP address. Ensure you can access your Immich instance via `http://your.domain.name` (note the **http**).

Your Immich installation must be accessible from the internet on TCP port 80 (for http challenge) or port 443 (for https/tls challenge). If you are running this on a home network, you will need to configure port forwarding on your router. A server hosted with a cloud provider typically won't require router port forwarding, but you may need to adjust firewall rules.

### Configure

Use snapd's configuration options to set `acme-domain` and `acme-email` to their appropriate values. The domain name should be the one pointing to your Immich installation. Please use a real email address, as it will be associated with your Let's Encrypt account. Let's Encrypt uses this email to send important notifications about your certificate, such as expiration warnings.

```sh 
sudo snap set immich-distribution acme-domain="your.domain.name"
sudo snap set immich-distribution acme-email="immich@example.com"
```

### Challenge Type

By default, certificates are issued over http, to use https, change `acme-challenge-type`.

```sh
sudo snap set immich-distribution acme-challenge-type="tls"
```

To revert to http challenge:

```sh
sudo snap set immich-distribution acme-challenge-type="http"
```

### Issue the certificate

The following command will attempt to register a Let's Encrypt account (if one doesn't exist for the email) and issue the certificate. It will also automatically enable HTTPS in Immich Distribution using this new certificate.

```sh
sudo immich-distribution.lets-encrypt
```

Try accessing your site via `https://your.domain.name`. If it loads successfully, you are all set! The certificate should renew automatically before it expires.

### Troubleshoot

**For HTTP-01 challenge (default):**

1. Ensure your Immich instance is accessible on port 80 from the public internet.
2. Requests to `http://your.domain.name/.well-known/acme-challenge/` must reach the Immich Distribution instance for the ACME challenge to succeed.

**For TLS-ALPN-01 challenge:**

1. Ensure your Immich instance is accessible on port 443 from the public internet.
2. Requests to `https://your.domain.name/.well-known/acme-challenge/` must reach the Immich Distribution instance for the ACME challenge to succeed. No HTTP access required.

**General troubleshooting:**

3. Check the HAProxy logs for errors: `journalctl -eu snap.immich-distribution.haproxy`.
4. You can re-run `sudo immich-distribution.lets-encrypt`. However, be aware of Let's Encrypt's rate limits if you run it too frequently.
5. For extended troubleshooting without hitting production rate limits, consider using the [Let's Encrypt staging environment](https://letsencrypt.org/docs/staging-environment/) by setting `sudo snap set immich-distribution acme-staging="true"` before running the command.

## Option 2: Manual Certificate Management

For self-signed certificates, existing certificates from other providers, or corporate PKI systems, you can manually place certificate files in the HAProxy directory.

### Using Manual Certificates

When `acme-domain` is not set, Immich Distribution will look for manually placed certificates. These certificates can be self-signed (for development/testing), obtained from another Certificate Authority, or managed through corporate PKI systems.

```sh
# Copy your certificate and private key to the HAProxy directory
sudo cp your-certificate.crt /var/snap/immich-distribution/common/acme/haproxy/cert.crt
sudo cp your-private-key.key /var/snap/immich-distribution/common/acme/haproxy/cert.crt.key

# Set permissions
sudo chown root:root /var/snap/immich-distribution/common/acme/haproxy/cert.crt*
sudo chmod 600 /var/snap/immich-distribution/common/acme/haproxy/cert.crt*

# Enable HTTPS (this will automatically restart HAProxy)
sudo snap set immich-distribution https-enabled="true"
```

### Generating Self-Signed Certificates

For development or testing purposes, you can generate your own self-signed certificate:

```sh
# Generate private key and certificate
sudo openssl genrsa -out your-private-key.key 2048
sudo openssl req -new -x509 -key your-private-key.key -out your-certificate.crt -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=your.domain.name"
```

Replace `your.domain.name` with your actual domain or IP address. After generating the certificate, follow the steps shown in the "Using Manual Certificates" section above.

### Certificate Renewal and Management

**Manual certificate renewal:**
Replace certificate files in the HAProxy directory and restart: `sudo snap restart immich-distribution.haproxy`

**Switch from ACME to manual:**
```sh
sudo snap unset immich-distribution acme-domain
# Place manual certificates as described above
sudo snap restart immich-distribution.haproxy
```

**Switch from manual to ACME:**
```sh
sudo snap set immich-distribution acme-domain="your.domain.name"
sudo snap set immich-distribution acme-email="your@email.com"
sudo immich-distribution.lets-encrypt
```

### Troubleshooting Manual Certificates

**Verify files and permissions:**
```sh
sudo ls -la /var/snap/immich-distribution/common/acme/haproxy/
```

**Check certificate validity:**
```sh
sudo openssl x509 -in /var/snap/immich-distribution/common/acme/haproxy/cert.crt -text -noout
```

**Check HAProxy logs:**
```sh
journalctl -eu snap.immich-distribution.haproxy
```

## Disable HTTPS

```sh
sudo snap set immich-distribution https-enabled="false"
```
