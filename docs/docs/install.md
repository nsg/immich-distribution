# Installation

``` bash title="Install Immich Distribution"
sudo snap install immich-distribution
```

The package can be installed from the snap store like any other snap package. The package is **huge** (over 700MB) so it can take some time to download. For more information see the [Snap Store](https://snapcraft.io/immich-distribution).

<iframe src="https://snapcraft.io/immich-distribution/embedded?channels=true" frameborder="0" width="100%" height="390px" style="border: 1px solid #CCC; border-radius: 2px;"></iframe>

??? Warning "Important information if you like to use candidate, beta or edge"

    The `edge` channel is not intended for end users, it contains experimental untested builds directly from the repository. The `beta` channel contains software that "works on my machine" and is published for general testing, expect things to break. I personally use `candidate` as a staging ground to try out a release for a few days before I push it to stable.

    Updates from "candidate to candidate", "stable to stable" or "stable to candidate" should always work. Otherwise I consider it a bug. The snap may contain migration logic that makes hard to downgrade, **never** downgrade a revision.

    ![](/assets/channel-flow.png)

    Feel free to use the `candidate` channel if you can't wait, but overall for a trouble free experience, stay at the default `stable` channel. Sounds complicated? Use the default `stable` channel.

## Prerequisites

### snapd

A computer running Linux with [support for snapd](https://snapcraft.io/docs/installing-snapd). Most commonly used Linux distributions are supported. If you do not have any strong preferences I recommends Ubuntu, or something Ubuntu based.

??? Info "Windows and WSL2"

    The snap *almost* works under Windows Subsystem for Linux. This is **not** a tested deployment but feel free to try it out if you are a Windows user. I did a quick test
    and noticed only a minor problem with the machine learning service.

### Hardware

A computer with a relatively modern Intel or AMD based CPU, for example the AVX instructionset is needed. You need **at minimum** 4GB available RAM, 6 or 8 is preferred. You probably also need a lot of free disk space, pictures are stored at `/var/snap`.

??? Note "What about ARM?"

    There is nothing technically blocking me from adapting this package for more architectures like ARM. At the moment I do not have any ARM based systems running to test and develop ARM support, so I have focused my resources on what I use personally.

### Used ports

Immich Distribution requires ports `80`, `443`, `3000-3003`, `5432`, `6379`, `8108` to be unused, only port 80 (and possible 443) needs to be available over the network. Immich will fail to start if they are used by another application.

??? Info "Used ports with service names"

    | Port | Interface | Comment |
    | ---- | --------- | ------- |
    | `80`   | all | HAProxy - Reverse proxy |
    | `443`  | all | HAProxy (only if HTTPS is enabled) |
    | `3000-3003` | all | Immich Services |
    | `5432` | lo | Postgres - Relation database |
    | `6379` | lo | Redis - In-memory KV database |
    | `8108` | lo | Typesense - Search database |

## Connecting to the server

![](/assets/immich-loading.png){ align=right .img-scale }

If you installed immich-distribution to a server with the IP `192.168.1.10` open a browser and navigate to `http://192.168.1.10`. The stack can take up to a minute to fully start, especially the machine learning components are slow to start.

See the official [Post Install Steps](https://immich.app/docs/install/post-install) will guide you to setup your account, and configure your mobile application.

If this installation is exposed to the public internet I stronly suggest that you set up [https](/configuration/https) and read the [security](/configuration/security) section.



