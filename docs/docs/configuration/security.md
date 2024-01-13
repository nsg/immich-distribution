# Security

This page collect security considerations related to Immich Distribution. Remember that the upstream Immich project is still early and actively developed so calibrate your expectations after that.

## Network Services

Immich is built as several discrete services communicating with each other over HTTP. Upstream Immich is built on the assumption that all processes are running inside a private network (inside Docker). This is not the case for this snap, it's contained inside a sandbox but the network is shared with the host.

!!! Danger "Important information if the OS is shared"

    If this system is shared with other untrusted users or processes consider deploying this inside a private network namespace, container or VM. It's possible to trigger unwanted API calls with a command like `curl http://127.0.0.1:3003/...`.

There are a few ports listening to all interfaces, I hope to fix this soon. But overall I recommend to configure a firewall and block ports `3000-3003` while you wait.

## Snapd Sandbox

If your Linux distribution fully supports all the security futures of snapd (like Ubuntu) the sandbox should keep processes running inside the `immich-distribution` package contained. Permissions are given per-application inside the package, but overall they are allowed to access the network, and listen on the network for incoming connections. No file system access outside the sandbox or any other special permissions are granted.

So overall if you configure your firewall limiting what Immich can access, it would be hard for a process running inside this package to do any harm to your server. A denial of service is of course always possible.

??? Note "Process Permissions"

    | Process | Permission | Description |
    | ------- | ---------- | ----------- |
    | psql | [network](https://snapcraft.io/docs/network-interface) | General network access |
    | postgres | [network-bind](https://snapcraft.io/docs/network-bind-interface) | Listen for incoming connections |
    | redis-server | [network-bind](https://snapcraft.io/docs/network-bind-interface) | Listen for incoming connections |
    | immich-server | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
    | immich-microservices | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
    | immich-web | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
    | immich-machine-learning | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
    | cli | [network](https://snapcraft.io/docs/network-interface) | General network access |
    | haproxy | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |
    | sync | [network](https://snapcraft.io/docs/network-interface) | General network access |
    | backup | - | |
    | import | - | |
    | acme | [network](https://snapcraft.io/docs/network-interface), [network-bind](https://snapcraft.io/docs/network-bind-interface) | General network access, Listen for incoming connections |

    Looking at your process list you may notice that several of the processes run as root, that can look scary, note that this is as root inside the sandbox with limited capabilities. The process is fully contained by the snapd sanbox.
    
    If you are curious you can jump in and inspect the sandbox by executing 

    ```sh
    sudo snap run --shell immich-distribution.{PROCESS}
    ```

### File Permissions

The sandbox do not only limit what the application can see, it's also greatly limits where it can write. `/var/snap/immich-distribution/common/` is used as a writable area where all the state is saved.

A process running inside a snap package only sees a limited view of your host system. `/` is based on a base image called "a core snap". Immich Distribution uses `core22` with is based on Ubuntu 22.04 LTS. A limited list of select paths are then exposed from the host by the snapd daemon, a snap package can request more paths to be exposed via permissions.

## TLS and HTTPS

Immich serves traffic over plain text HTTP, you can issue let's encrypt certificates and configure haproxy to use them to encrypt all traffic leaving the server. For more information see [configure HTTPS](/configuration/https)

No internal traffic is encrypted, traffic is only sent locally via the loopback (lo, 127.0.0.1) interface so an external observer will not be able to listen in. This can be a security consideration if you have untrusted users or software running on the same server.
