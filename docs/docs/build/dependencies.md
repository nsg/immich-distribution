# Package dependencies

I use this page to track custom built deb-packages that I have built as a dependency for Immich Distribution. The packages are build in clean containers targeting Ubuntu 22.04.

## Repository

```
deb [signed-by=/etc/apt/trusted.gpg.d/nsg.gpg] https://nsg.github.io/aptly/deb ./
```

You can import the GPG key with: `curl -Ls https://nsg.github.io/aptly/nsg.gpg | gpg --dearmor -o /etc/apt/trusted.gpg.d/nsg.gpg`

For more information and available packages, visit: [https://nsg.github.io/aptly/](https://nsg.github.io/aptly/).

## Package dependency

### libvips

```mermaid
flowchart LR

subgraph Immich
    sharp
end

nsg-cgif --- nsg-libvips
nsg-libraw --- nsg-imagemagick
nsg-x265 --- nsg-imagemagick
nsg-x265 --- nsg-libheif
nsg-libde265 --- nsg-libheif
nsg-libde265 --- nsg-imagemagick
nsg-libheif --- nsg-imagemagick
nsg-libheif --- nsg-libvips
nsg-imagemagick --- nsg-libvips
nsg-libvips -.- sharp
```

Immich uses sharp for image processing. Sharp uses libvips, and libvips has imagemagick as a backend and uses it as a fallback engine if it can't handle an image format directly.

### VectorChord

```mermaid
flowchart LR

subgraph Immich
    server
end

nsg-vectorchord --- nsg-pgvector
nsg-vectorchord --- nsg-postgres
nsg-pgvector --- nsg-postgres
nsg-postgres -.- server
```

### Immich Distribution

```mermaid
flowchart TD

subgraph Immich
    Server
    Web
    machine-learning["Machine Learning"]
end


subgraph ID["Immich distribution"]
    Immich
    Server
    Scripts
    Sync
end

nsg-redis --- Server
nsg-postgres --- Server
nsg-libvips --- Server
nsg-vectorchord --- Server

nsg-python --- machine-learning
nsg-mimalloc --- machine-learning

nsg-haproxy --- Scripts
nsg-lego --- Scripts

nsg-python --- Sync
```
