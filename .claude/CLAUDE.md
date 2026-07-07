# Immich Snap Distribution

Snap package for [Immich](https://github.com/immich-app/immich). Base: `core22` (Ubuntu 22.04). Strict confinement. Version in `VERSION` file, bumped via automated `bump/*` branch PRs (reviewed with the `/verify-release` command). Upstream is Docker-based; mapping it onto snapd sometimes requires creative thinking. All deps must exist in Ubuntu 22.04 repos or the custom APT repo. User config via `snap set/get` and hooks.

## Gotchas

### Custom APT Repository (`nsg-*` packages)
An externally managed APT repo (`https://nsg.github.io/aptly/deb`) provides `nsg-redis`, `nsg-libvips`, `nsg-postgres`, `nsg-pgvector`, `nsg-vectorchord`, `nsg-mimalloc`, `nsg-haproxy`, `nsg-lego` (plus `nsg-imagemagick`, `nsg-libheif`, `nsg-cgif` pulled in as deps of `nsg-libvips`). These mirror deps from upstream Docker images (`immich-app/base-images`); when upstream bumps deps, the APT packages usually need bumping too. Sources live in the gitignored local clone `upstream/aptly/` (`ARG VERSION=` in each `<package>/Containerfile` is the published version). If the repo is down or the GPG key (`snap/keys/5C61B36E.asc`) expires, builds fail with no fallback.

### Hardcoded Library Versions in Snap Layouts
Layout symlinks in `snap/snapcraft.yaml` hardcode versions (`vips-modules-8.17`, `ImageMagick-7.1.2`) that must match the actual `nsg-libvips`/`nsg-imagemagick` versions. A mismatch silently breaks image processing: ImageMagick can't find delegates/coders, vips can't load format plugins, RAW/TIFF thumbnails fail via the vips magick fallback loader. `tests/test_vips_version.py` validates against the APT repo.

### Sharp / Libvips HEIC Support
Sharp prefers its own bundled libvips, which lacks HEIC — breaking photo imports from many phones. It must link against the system `nsg-libvips`. Most historical workarounds have been removed; watch for regressions on upgrades.

### Patches Against Upstream
`parts/immich-server/patches/` (applied `git apply -p1`): pg_dumpall path, CLI command for admin API key, log spam removal. There is no standalone patch check — a patch that no longer applies fails the snap build in CI.

### extism-js GLIBC Pinning
The plugins build seds `extism-js` down to 1.3.0, the last GLIBC 2.35 (Ubuntu 22.04) compatible version; newer versions need GLIBC ≥2.39. A grep check fails the build if upstream changed the version string and the sed missed.

### Tied to core22 (glibc 2.35)
The `node/24` snap is built on `core24` (needs glibc ≥2.38) and cannot run on our base; the Node channel is pinned in `snap/snapcraft.yaml`.

### ML is CPU-Only, on uv Python 3.12
Built with `cpu` extras only (no CUDA), running on a uv-installed CPython 3.12 (`uv-python312` part) — not the core22 system Python. `libmimalloc.so.2` is preloaded via `LD_PRELOAD` — the version in the path must match the `nsg-mimalloc` package.

### Pinned External Dependencies
Pinned with checksums, break if removed/republished upstream: `jellyfin-ffmpeg7` deb (tied to `jammy`), `uv` (version + SHA256), test assets (pinned commit in `.github/actions/fetch-test-assets/`).

### Era-Based Upgrade Protection
`snap/hooks/post-refresh` blocks upgrades that skip an era (`IMMICH_DISTRIBUTION_ERA` in `src/bin/load-env`, currently `2`). Escape hatches: touching `$SNAP_COMMON/no-pre-refresh-hook` or `$SNAP_COMMON/no-post-refresh-hook` disables the hooks.

### Privilege Dropping (snap_daemon)
Data-touching operations must run as `snap_daemon`, via `drop_privileges` in `src/bin/load-env`. Postgres refuses to start if `$SNAP_COMMON/pgsql` ownership is wrong; the configure hook `chown`s it on every run.

### `upstream/` Is Not a Submodule
`upstream/` is gitignored scratch clones (`immich`, `aptly`). Must be manually cloned and checked out at the right tag for patch generation/validation and `update.sh` to work. Fetching/checking out tags there is always fine.

## AI Behavior
- Gather context before changes. Be concise.
- **NEVER commit without the user explicitly asking to commit.** Not after making changes, not as part of a workflow, not "while you're at it".
- Minimal code comments, no extra files unless requested.
