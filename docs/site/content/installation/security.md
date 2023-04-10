+++
title = "Security"
weight = 2
+++

# Security

This page collect security considerations related to Immich Distribution.

## Services

Immich is built as several discrete services communicating with each other over HTTP. Web and server are supposed to be exposed so they should be safe, but 3002 and 3003 are expected to be local and they are not properly secured. You should firewall them if they are exposed.

| Service | Port | Interface | Auth |
| ------- | ---- | --------- | ---- |
| Immich Web | 3000 | all | Yes |
| Immich Server | 3001 | lo | Yes |
| Immich Microservices | 3002 | all | No |
| Immich Machine Learning | 3003 | all | No |

**Note**: The services should be modified to only listen on localhost. It's possible that I need to maintain a patch for this.

## Databases

| Service | Port | Interface | Auth |
| ------- | ---- | --------- | ---- |
| Postgres | 5432 | lo | Yes |
| Redis | 6379 | lo | No |
| Typesense | 8108 | lo | Yes |

**Note**: Redis do support auth, I should configure and use it.

## Snapd sandbox

If your Linux distribution fully supports all the security futures of snapd the sandbox should keep processes running inside the immich-distribution package contained. Permissions are given per-application inside the package, but overall they are allowed to access the network, and listen on the network for incoming connections. No file system access or any other special permissions are granted.

| Process | Permission |
| ------- | ---- |
| psql | network |
| postgres | network-bind |
| redis-server | network-bind |
| typesense | network-bind |
| immich-server | network, network-bind |
| immich-microservices | network, network-bind |
| immich-web | network, network-bind |
| immich-machine-learning | network, network-bind |
| cli | network |
| haproxy | network, network-bind |
| sync | network |
| backup | - |
| import | - |
| acme | network, network-bind |

Several of the processes runs as UIO 0 (root), the process is contained by the snapd sanbox. If you are curious you can inspect the sanbox by executing 

```sh
sudo snap run --shell immich-distribution.{PROCESS}
```

### Folders

The sandbox do not only limit what the application can see, it's also greatly limits where it can write. `/var/snap/immich-distribution/common/` is used as a writable area where all the state is saved.

## TLS and HTTPS

Immich serves traffic over plain text HTTP, you can issue let's encrypt certificates and configure haproxy to use them to encrypt all traffic leaving the server. For more information see [configure HTTPS](@/configuration/https.md)

No internal traffic is encrypted, traffic is only sent locally via the loopback (lo, 127.0.0.1) interface.
