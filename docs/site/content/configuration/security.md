+++
title = "Security"
+++

# Security

This page collects security considerations related to Immich Distribution. Remember that the upstream Immich project is still in early and active development, so please calibrate your expectations accordingly.

## Network Services

Immich is built as several discrete services communicating with each other over HTTP. Upstream Immich assumes all its processes run within a private network (typically inside Docker). This is not the case for this Snap package; while it's contained within a sandbox, the network is shared with the host system.

{% admonition(type="danger", title="Important information if the OS is shared") %}
If this system is shared with other untrusted users or processes, consider deploying Immich Distribution inside a private network namespace, container, or virtual machine. It's possible for local users or processes to trigger unwanted API calls, for example, using a command like `curl http://127.0.0.1:3003/...`.
{% end %}

## Snapd Sandbox

If your Linux distribution fully supports all of snapd's security features (like Ubuntu), the sandbox should effectively contain processes running within the `immich-distribution` package. Permissions are granted per-application within the package. Overall, they are allowed to access the network and listen for incoming connections. No file system access outside the sandbox or other special permissions are granted by default.

Therefore, if you configure your firewall to limit what Immich can access, it would be difficult for a process within this package to harm your server. However, a denial-of-service attack is always a possibility.

{% admonition(type="note", title="Process Permissions", collapsible=true) %}
| Process | Permission | Description |
| ------- | ---------- | ----------- |
| psql | [network](https://snapcraft.io/docs/network-interface) | General network access |
| postgres | [network-bind](https://snapcraft.io/docs/network-bind-interface) | Listen for incoming connections |
| redis-server | [network-bind](https://snapcraft.io/docs/network-bind-interface) | Listen for incoming connections |
| immich-server | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
| immich-machine-learning | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
| haproxy | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
| sync | [network](https://snapcraft.io/docs/network-interface) | General network access |
| backup | - | |
| import | - | |
| acme | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |

When inspecting your process list, you might notice several processes running as root. This can appear concerning, but note that this is root *inside* the sandbox, with limited capabilities. The processes are fully contained by the snapd sandbox.
    
If you are curious, you can inspect the sandbox environment by executing:

```sh
sudo snap run --shell immich-distribution.{PROCESS}
```
{% end %}

### File Permissions

The sandbox not only limits what the application can see but also greatly restricts where it can write. The directory `/var/snap/immich-distribution/common/` is used as a writable area where all application state is saved.

A process running inside a Snap package has a limited view of your host system. Its root filesystem (`/`) is based on a base image known as a "core snap". Immich Distribution uses `core22`, which is based on Ubuntu 22.04 LTS. The snapd daemon then exposes a limited list of selected paths from the host system. A Snap package can request additional paths to be exposed via permissions.

## TLS and HTTPS

By default, Immich serves traffic over plain text HTTP. You can issue Let's Encrypt certificates and configure HAProxy to use them, thereby encrypting all traffic leaving the server. For more information, see [Configure HTTPS](/configuration/https).

Internal traffic between Immich services is not encrypted. This traffic is sent locally via the loopback interface (lo, 127.0.0.1), so an external observer cannot intercept it. However, this could be a security consideration if untrusted users or software are running on the same server.
