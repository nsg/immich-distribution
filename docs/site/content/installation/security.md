+++
title = "Security"
weight = 2
+++

# Security

This page collect security considerations related to Immich Distribution.

## Network Services

Immich is built as several discrete services communicating with each other over HTTP. Upstream Immich is built on the assumption that all processes are running inside a private network (inside Docker). This is not the case for this snap, it's contained inside a sandbox but the network is shared with the host.

If this system is shared with other untrusted users or processes consider deploying this inside a private network namespace. For example by launching a container or VM. I personally run this in a [LXD container](https://linuxcontainers.org/lxd/introduction/), but anything that do not interfere with snapd should work.

There are a few ports listening to all interfaces, I hope to fix this soon. But overall I recommend to configure a firewall and block ports `3000-3003` while you wait.

## Snapd Sandbox

If your Linux distribution fully supports all the security futures of snapd the sandbox should keep processes running inside the immich-distribution package contained. Permissions are given per-application inside the package, but overall they are allowed to access the network, and listen on the network for incoming connections. No file system access or any other special permissions are granted.

So overall if you configure your firewall limiting what Immich can access, it would be hard for a process running inside this package to do any harm to your server.

### Process Permissions

| Process | Permission |
| ------- | ---- |
| psql | [network](https://snapcraft.io/docs/network-interface) |
| postgres | [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| redis-server | [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| typesense | [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| immich-server | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| immich-microservices | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| immich-web | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| immich-machine-learning | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| cli | [network](https://snapcraft.io/docs/network-interface) |
| haproxy | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) |
| sync | [network](https://snapcraft.io/docs/network-interface) |
| backup | - |
| import | - |
| acme | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) |

Looking at your process list you may notice that several of the processes run as root, that can look scary, note that this is as root inside the sandbox with limited capabilities. The process is fully contained by the snapd sanbox. If you are curious you can inspect the sandbox by executing 

```sh
sudo snap run --shell immich-distribution.{PROCESS}
```

### File Permissions

The sandbox do not only limit what the application can see, it's also greatly limits where it can write. `/var/snap/immich-distribution/common/` is used as a writable area where all the state is saved.

A process running inside a snap package only sees a limited view of your host system. `/` is based on a base image called "a core snap". Immich Distribution uses `core20` with is based on Ubuntu 20.04 LTS. A limited list of select paths are then exposed from the host my the snapd daemon, a snap package can request more paths to be exposed via permissions.

## TLS and HTTPS

Immich serves traffic over plain text HTTP, you can issue let's encrypt certificates and configure haproxy to use them to encrypt all traffic leaving the server. For more information see [configure HTTPS](@/configuration/https.md)

No internal traffic is encrypted, traffic is only sent locally via the loopback (lo, 127.0.0.1) interface so an external observer will not be able to listen in. This can be a security consideration if you have untrusted users or software running on the same server.
