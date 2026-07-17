+++
title = "Package dependencies"
+++

# Package dependencies

I use this page to track custom built deb-packages that I have built as a dependency for Immich Distribution. The packages are built in clean containers targeting Ubuntu 22.04.

## Repository

```
deb [signed-by=/etc/apt/trusted.gpg.d/nsg.gpg] https://nsg.github.io/aptly/deb ./
```

You can import the GPG key with: `curl -Ls https://nsg.github.io/aptly/nsg.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/nsg.gpg`

For more information and available packages, visit: [https://nsg.github.io/aptly/](https://nsg.github.io/aptly/).

## Package dependency

### libvips

![Dependency tree where nsg-cgif, nsg-libheif and nsg-imagemagick feed into nsg-libvips, used by sharp inside Immich](/assets/deps-libvips.svg)

Immich uses sharp for image processing. Sharp uses libvips, and libvips has imagemagick as a backend and uses it as a fallback engine if it can't handle an image format directly.

### VectorChord

![Dependency tree where nsg-vectorchord and nsg-pgvector build on nsg-postgres, used by the Immich server](/assets/deps-vectorchord.svg)

### Immich Distribution

![Overview of nsg packages feeding the Immich server, machine learning, and the distribution scripts](/assets/deps-overview.svg)
