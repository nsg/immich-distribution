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

Immich Distribution requires ports `3000-3003`, `5432`, `6379` and `8108` to be unused, port `80` is also required by default, and port `443` if you enable https. See [HAProxy](configuration/haproxy.md) if you like to change the http or https ports. Immich will fail to start if these ports are used by another application.

??? Info "Used ports with service names"

    | Port | Interface | Configurable | Comment |
    | ---- | --------- | ------------ | ------- |
    | `80`   | all | YES | HAProxy - Reverse proxy |
    | `443`  | all | YES | HAProxy (only if HTTPS is enabled) |
    | `3000-3003` | all | NO | Immich Services |
    | `5432` | lo | NO | Postgres - Relation database |
    | `6379` | lo | NO | Redis - In-memory KV database |
    | `8108` | lo | NO | Typesense - Search database |

## Connecting to the server

![](/assets/immich-loading.png){ align=right .img-scale }

If you installed immich-distribution to a server with the IP `192.168.1.10` open a browser and navigate to `http://192.168.1.10`. The stack can take up to a minute to fully start, especially the machine learning components are slow to start.

See the official [Post Install Steps](https://immich.app/docs/install/post-install) will guide you to setup your account, and configure your mobile application.

If this installation is exposed to the public internet I stronly suggest that you set up [https](/configuration/https) and read the [security](/configuration/security) section.

## Updates

Updates are by **default** automatic, this is a core concept of the package format. I write the software with that in mind so I will never push a breaking change. You should never have a broken system as a result of an automatic update.

??? Note "Disable or control automatic updates"

    The advantages with automatic updates usually outweights the disadvantages for ordinary users, that's why automatic updates are on by default. If you have other needs this behavior can be changed with the following commands.

    **Please note** that if you do not update regularly (that's about once a week, at minimum) I can't guarantee that updates are completely trouble free. They should be, but I test only updates done sequentially from version to version.
    
    ```bash title="Prevent updates over the weekend"
    snap refresh --hold=72h immich-distribution # (1)
    ```

    1. Change this to a value to your likeing. See the [documentation](https://snapcraft.io/docs/keeping-snaps-up-to-date) for more information.

    ```bash title="Never update automatically"
    snap refresh --hold=forever immich-distribution
    ```

    Another alternative is to pick a time when updates are applied, like in the middle in the night. For more information about that, and much more see [snapd:s documentation](https://snapcraft.io/docs/keeping-snaps-up-to-date).

**Do not expect me to release updates the same day** as an upstream Immich release. I hope to do so in a **reasonable time**. When Immich releases an update I will build and push an update to the candidate channel when I beleave I got it right (my server uses this channel) and try it out myself for a few days. I will relese the build to the stable channel after a few days, if everyting works.

??? Note "When is the next update released?"

    Updates can be quick and easy, or a lot of work depending on the changes upstream. I will open a tracking issue tagged with [new-version](https://github.com/nsg/immich-distribution/issues?q=is%3Aissue+is%3Aopen+label%3Anew-version) when I detect an update, feel free to ask questions there. If you have experience with building snap packages, see [upgrade](/build/upgrade) how to contribute to the project.

    To speed up the transition time from "beta -> candidate -> stable", help me test the build and inform me about detected problems, try to troubleshoot them, and of course, also report success!

    Finally, just a thumbs up or any message will keep me motivated to carry on!

## Configuration

By default you should have a working installation of Immich, but you may like to configure it a bit. See the [configuration](/configuration/) pages for that.
