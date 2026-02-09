# Immich Snap Distribution

Snap package for [Immich](https://github.com/immich-app/immich). Base: `core22` (Ubuntu 22.04, Python 3.10). Strict confinement. Version in `VERSION` file, bumped via `bump/*` branch PRs.

## Structure

- `snap/snapcraft.yaml` (build/deps/services/plugs)
- `snap/hooks/` (install/configure)
- `src/bin/` (scripts and wrappers)
- `src/etc/` (config templates)
- `parts/immich-server/patches/` (upstream patches)
- `upstream/immich/` (upstream code)
- `tests/` (pytest/scripts)
- `workflows/` (release automation)
- `.github/workflows/` (CI).

Confined with specific plugs. Config via `snap set/get`, hooks, env vars. All deps must exist in Ubuntu 22.04 repos.

## Gotchas

Upstream `immich-app/immich` is based around Docker, this package is based around `snapd` and this requires sometime some creative thinking.

### Custom APT Repository (`nsg-*` packages)
An externally managed APT repo (`https://nsg.github.io/aptly/deb`) provides `nsg-redis`, `nsg-libvips`, `nsg-postgres`, `nsg-pgvector`, `nsg-vectorchord`, `nsg-mimalloc`, `nsg-haproxy`, `nsg-lego`. These mirror deps from upstream Docker images. When upstream bumps deps, the APT repo packages usually need bumping too. If the repo is down or the GPG key (`snap/keys/5C61B36E.asc`) expires, builds fail with no fallback.

### Hardcoded Library Versions in Snap Layouts
`snap/snapcraft.yaml` has layout symlinks with hardcoded versions: `vips-modules-8.17`, `ImageMagick-7`, `ImageMagick-7.1.1`. These must stay in sync with the actual `nsg-libvips` and ImageMagick versions. A version mismatch silently breaks image processing. `tests/test_vips_version.sh` validates vips but not ImageMagick.

### Sharp / Libvips HEIC Support
Sharp (the Node.js libvips wrapper) has historically been a pain point. It tends to use its own bundled libvips binary which lacks HEIC support, breaking photo imports from many phones. Past versions required extensive workarounds to force Sharp to link against the system `nsg-libvips` (which includes HEIC). Sharp has improved and most workarounds have been removed, but watch for regressions on upgrades.

### Patches Against Upstream
Patches in `parts/immich-server/patches/` modify upstream server code (pg_dumpall path, CLI commands for admin API key and media location, log spam removal). Mixed formats: `pg_dumpall-path.path` uses `patch -p0`, others use `git apply -p1`. Patches break when upstream refactors the patched files. Use `tests/validate-patch.sh <patch_file> <target_file>` to validate a patch applies cleanly against the upstream checkout (requires `upstream/immich/` at the correct tag). The Makefile `test` target also runs `git apply --check` on all patches.

### extism-js GLIBC Pinning
The plugins build (`snap/snapcraft.yaml`) uses `sed` to downgrade `extism-js` from the upstream version to 1.3.0 (last GLIBC 2.35/Ubuntu 22.04 compatible version). Both the source and target version strings are hardcoded in the sed. A `grep` check fails the build if the replacement didn't match, so upstream version changes are caught early.

### Sync Service Custom DB Objects
`src/etc/modify-db.sql` creates custom tables (`assets_delete_audits`, `assets_filesync_lookup`) and a trigger on the upstream `asset` table. These could conflict with upstream Immich migrations that modify the `asset` table schema.

### Hardcoded Python 3.10 Path
`src/bin/sync-service.sh` hardcodes `python3.10` in `PYTHONPATH`. Tied to `core22` (Ubuntu 22.04). Breaks silently if base changes to `core24` (Python 3.12).

### ML is CPU-Only
Machine learning is built with `cpu` extras only (no CUDA/GPU). `libmimalloc.so.2` is preloaded via `LD_PRELOAD` - version in path must match the `nsg-mimalloc` package.

### Pinned External Dependencies
Several deps are pinned with checksums and break if removed/republished: `jellyfin-ffmpeg7` deb (tied to `jammy`), `uv` (Python installer, version + SHA256), `pgvecto.rs` deb (pinned to PG15), test assets (pinned git commit). Node.js comes from `node/20/stable` snap channel (EOL April 2026).

### Era-Based Upgrade Protection
`snap/hooks/post-refresh` blocks skipping eras (currently era `1` in `src/bin/load-env`). Users cannot skip intermediate era versions. Escape hatches: touching `$SNAP_COMMON/no-pre-refresh-hook` or `$SNAP_COMMON/no-post-refresh-hook` disables hooks entirely.

### Privilege Dropping (snap_daemon)
Snap services run as root by default. Postgres and other services must run as unprivileged user `snap_daemon` (declared as `system-usernames: snap_daemon: shared`). All data-touching operations use `drop_privileges` (`src/bin/load-env`) which calls `setpriv` to switch to `snap_daemon`. File ownership on `$SNAP_COMMON/pgsql` must be correct or postgres refuses to start. The configure hook `chown`s it on every run.

### Snap Layouts: Path Redirection
Snap strict confinement means the filesystem is read-only and restricted. Snap layouts in `snapcraft.yaml` create symlinks so libraries and apps find their files at expected paths. Key redirections: ImageMagick config/modules (`/usr/etc/ImageMagick-7`, `/usr/lib/ImageMagick-7.1.1`), vips modules (`/usr/lib/vips-modules-8.17`), upload directory (`$SNAP/usr/src/app/upload` → `$SNAP_COMMON/upload`). Without these, ImageMagick can't find its delegates/coders and vips can't load format plugins. This is a common snap packaging challenge - libraries with hardcoded paths need layout entries.

### Upload Path Symlink
The manager auto-migrates legacy paths (`/usr/src/app/upload`, `/data`, etc.) in the database for Docker-to-snap migrations.

### `upstream/` Is Not a Submodule
`upstream/` is gitignored. It's a local clone for patch development and `update.sh`. Must be manually cloned and checked out at the right tag for patch generation/validation to work.

## Commands

```bash
# Versions
CURRENT=$(cat VERSION | tr -d '[:space:]')
PREVIOUS=$(git show $(git log --oneline -2 VERSION | tail -1 | cut -d' ' -f1):VERSION | tr -d '[:space:]')
cd upstream/immich && git fetch --tags --quiet origin && cd -

# Upstream release notes (use any version, e.g. v$CURRENT or v$PREVIOUS)
gh release view v$CURRENT --repo immich-app/immich
gh release view v$CURRENT --repo immich-app/immich --json body --jq .body | grep -i '<term>'

# Upstream changes (run in upstream/immich)
git log --oneline --no-merges v$PREVIOUS..v$CURRENT | head -20
git log --oneline --no-merges v$PREVIOUS..v$CURRENT -- server/
git log --oneline --no-merges v$PREVIOUS..v$CURRENT -- machine-learning/
git log --oneline --no-merges --grep="<term>" v$PREVIOUS..v$CURRENT
git log --oneline --no-merges --author="<name>" v$PREVIOUS..v$CURRENT
git diff --dirstat=files,10 v$PREVIOUS..v$CURRENT
git diff --stat v$PREVIOUS..v$CURRENT | tail -1
git log --pretty=format: --name-only v$PREVIOUS..v$CURRENT | sort | uniq -c | sort -rn | head -20  # top changed files

# Patch impact
ls -1 parts/immich-server/patches/
cd upstream/immich && git log --oneline --no-merges v$PREVIOUS..v$CURRENT -- <path-from-patch>

# CI build inspection
BRANCH=$(git branch --show-current)
RUN_ID=$(gh run list --branch "$BRANCH" --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view $RUN_ID                # summary
gh run view $RUN_ID -v             # verbose with steps
gh run view $RUN_ID --json jobs --jq '.jobs[] | "[\(.conclusion // "running" | ascii_upcase)] \(.name)"'
gh ext run-logs $RUN_ID  # outputs a file path to a zip, unpack that and read the log files. ONLY way to get build logs. --log, --log-failed, and API downloads are all broken.
```

## Version Bump Workflow

On `bump/*` branches: CI runs extensive tests. One issue per minor (1.x), one PR per patch (1.2.x). The PR matching the branch has test results and monitored file diffs to review. Always check upstream `immich-app/immich` release notes. Docker breaking changes may not affect us - be critical. On failures, also check deps: base image, other `immich-app` org repos we depend on.

## AI Behavior
- Gather context before changes. Be concise. Discuss before committing.
- Minimal code comments, no extra files unless requested.
