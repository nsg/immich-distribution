# Installation

The package can be installed from the snap store like any other snap package, below is the CLI command to install Immich. You can of course use Software / App Center to install is as well.

``` bash title="Install Immich Distribution"
sudo snap install immich-distribution
```

The package is over 700MB so it can take some time to download. For more information see the [Snap Store](https://snapcraft.io/immich-distribution). Also checkout the prerequisites below.

[![Link to the Snapcraft Store](/assets/button.png){ class="center-image" }](https://snapcraft.io/immich-distribution)

## Available versions

{{snapstore_versions}}

!!! Warning "Important information if you like to use candidate, beta or edge"

    The `edge` channel is not intended for end users, it contains experimental untested builds directly from the repository. The `beta` channel contains software that "works on my machine" and is published for general testing, expect things to break. I personally use `candidate` as a staging ground to try out a release for a few days before I push it to stable.

    Updates from "candidate to candidate", "stable to stable" or "stable to candidate" should always work. Otherwise I consider it a bug. The snap may contain migration logic that makes hard to downgrade, **never** downgrade a revision.

    ![](/assets/channel-flow.png)

    Feel free to use the `candidate` channel if you can't wait, but overall for a trouble free experience, stay at the default `stable` channel. Sounds complicated? Use the default `stable` channel.

## Demo

[![Link to the Snapcraft Store](/assets/youtube-install-demo.jpg){ class="center-image" }](https://www.youtube.com/watch?v=LpOpgl2xAK0)

## Prerequisites

### snapd

A computer running Linux with [support for snapd](https://snapcraft.io/docs/installing-snapd). Most commonly used Linux distributions are supported. If you do not have any strong preferences I recommends Ubuntu, or something Ubuntu based.

??? Info "Windows and WSL2"

    The snap *almost* works under Windows Subsystem for Linux. This is **not** a tested deployment but feel free to try it out if you are a Windows user. I did a quick test
    and noticed only a minor problem with the machine learning service.

### Hardware

A computer with a relatively modern Intel or AMD based CPU. You need **at minimum** 4GB available RAM, 6 or 8 is preferred. You probably also need a lot of free disk space, pictures are stored at `/var/snap`.

??? Note "What about ARM?"

    There is nothing technically blocking me from adapting this package for more architectures like ARM. At the moment I do not have any ARM based systems running to test and develop ARM support, so I have focused my resources on what I use personally.

    If you like to comment, chat or vote for ARM support please do a :thumbsup: or write an comment [at this issue](https://github.com/nsg/immich-distribution/issues/192).

### Used ports

Immich Distribution requires ports `3001-3003`, `8081-8082`, `5432` and `6379` to be unused, port `80` is also required by default, and port `443` if you enable https. It also allocates free ports in the `34000-36000` range.
See [HAProxy](configuration/haproxy.md) if you like to change the http or https ports. Immich will fail to start if these ports are used by another application.

??? Info "Used ports with service names"

    | Port | Interface | Configurable | Comment |
    | ---- | --------- | ------------ | ------- |
    | `80`   | all | YES | HAProxy - Reverse proxy |
    | `443`  | all | YES | HAProxy (only if HTTPS is enabled) |
    | `3001-3003` | lo | NO | Immich Services |
    | `8081-8082` | all | NO | Metrics (Prometheus) |
    | `5432` | lo | NO | Postgres - Relation database |
    | `6379` | lo | NO | Redis - In-memory KV database |
    | `34000-36000` | all | YES | ACME certificate renewals (if enabled) |

    **Note**: Immich Distribution allocates unused ports in the range `34000-36000`. The entire range will of course not be used.

## Connecting to the server

![](/assets/immich-loading.png){ align=right .img-scale }

After installing Immich Distribution, the services will start automatically in the background. You can access Immich through your web browser by navigating to:

- **If installed on your local computer:** Open `http://localhost` in your web browser
- **If installed on a remote server:** Open `http://SERVER-IP-ADDRESS` in your web browser (replace SERVER-IP-ADDRESS with the actual IP address of your server)

For example, if you installed immich-distribution on a server with the IP address `192.168.1.10`, you would navigate to `http://192.168.1.10` in your browser.

The official [Post Install Steps](https://immich.app/docs/install/post-install) will guide you to setup your account, and how to configure your mobile application.

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

    Updates can be quick and easy, or a lot of work depending on the changes upstream. A tracking issue tagged with [new-version](https://github.com/nsg/immich-distribution/issues?q=is%3Aissue+is%3Aopen+label%3Anew-version) should appear when an update is detected, feel free to ask questions there. If you have experience with building snap packages, see [upgrade](/build/upgrade) how to contribute to the project.

    To speed up the transition time from "candidate to stable", help me test the build and inform me of problems, try to troubleshoot them, and of course, also report success! Finally, just a thumbs up or any message will keep me motivated to carry on!

### Mobile app

If you use the mobile application you have probably installed it from [Google Play Store](https://play.google.com/store/apps/details?id=app.alextran.immich), [Apple App Store](https://apps.apple.com/us/app/immich/id1613945652) or [F-Droid](https://f-droid.org/packages/app.alextran.immich). These stores usually update the apps automatically in the background. It's rare, but if there is a breaking change in the API the mobile app may temporary break if there is a version mismatch between the mobile app and the server.

## Configuration

You should have a working installation of Immich out of the box, but you may like to configure it a bit. See the [configuration](/configuration/) pages for that.
