# Core22 → Core24 Migration Assessment

**Difficulty: Moderate-to-Hard**

The snap code changes themselves are straightforward, but the **external dependency rebuilds** make this a significant effort.

## Easy Changes (trivial code edits)

| Change | File |
|--------|------|
| `base: core22` → `core24` | `snap/snapcraft.yaml` |
| `architectures:` → `platforms:` syntax | `snap/snapcraft.yaml` |
| `python3.10` → `python3.12` in PYTHONPATH | `src/bin/sync-service.sh` |
| Remove/update extism-js GLIBC 2.35 pin (2.39 available) | `snap/snapcraft.yaml` |
| Update docs referencing core22/22.04 | `docs/` |

## Medium Changes (require investigation + testing)

| Change | Risk | Notes |
|--------|------|-------|
| `snap_daemon` → `_daemon_` (new system username) | **High** | UID changes from 584788 → 584792. All data in `$SNAP_COMMON` (especially `pgsql/`) is owned by old UID. Need migration hook to `chown` everything. If missed, **PostgreSQL refuses to start**. |
| `jellyfin-ffmpeg7` deb | Medium | Currently pinned to `-jammy`. Need a `-noble` build or verify jammy binary works on noble. |
| Stage package version changes | Medium | Some packages change soname: `libvpx7`→`libvpx9`, `libx264-163`→`libx264-164`, `libx265-199`→`libx265-209`, `libllvm15`→`libllvm18`, etc. Each needs verification. |
| Layout version paths | Medium | `vips-modules-8.17`, `ImageMagick-7.1.1` hardcoded — must match whatever the rebuilt nsg-libvips ships. |

## Hard Changes (external work required)

| Change | Effort | Notes |
|--------|--------|-------|
| **Rebuild all 8 `nsg-*` packages for Noble** | **Major** | `nsg-redis`, `nsg-libvips`, `nsg-postgres`, `nsg-pgvector`, `nsg-vectorchord`, `nsg-mimalloc`, `nsg-haproxy`, `nsg-lego` — all built against jammy. Must be rebuilt targeting noble. This is the single biggest blocker. |

## Key Risks

1. **`snap_daemon` UID migration** — Existing user data is owned by UID 584788. The new `_daemon_` user is UID 584792. A post-refresh hook must detect and re-chown, or users lose access to their database and uploads.

2. **NSG package rebuild** — The entire custom APT repository needs noble-targeted builds. Until that's done, nothing else matters. No fallback exists.

3. **Silent failures** — Python path, libmimalloc `.so.2` version, ImageMagick layout paths all fail silently if wrong. Good test coverage is essential.

4. **`snapcraft try` unavailable** — core24 doesn't support `snapcraft try`, making iterative development slower (full builds required).

## Snapcraft YAML Syntax Changes

### `architectures` → `platforms`

**Current (core22):**
```yaml
architectures:
  - build-on: [amd64]
    build-for: [amd64]
```

**Required (core24):**
```yaml
platforms:
  amd64:
```

### `snap_daemon` → `_daemon_`

**Current (core22):**
```yaml
system-usernames:
  snap_daemon: shared
```

**Required (core24):**
```yaml
system-usernames:
  _daemon_: shared
```

All scripts referencing `snap_daemon` (load-env, configure hook, etc.) must be updated.

### Environment Variables

| Deprecated (removed in core24) | Replacement |
|---|---|
| `CRAFT_ARCH_TRIPLET` | `CRAFT_ARCH_TRIPLET_BUILD_FOR` |
| `CRAFT_TARGET_ARCH` | `CRAFT_ARCH_BUILD_FOR` |

Neither is currently used in this project, so no change needed.

### Already Done

- `craftctl` is already used (not the removed `snapcraftctl`)

## Package Version Differences (22.04 → 24.04)

| Package | core22 (Jammy) | core24 (Noble) |
|---------|---------------|----------------|
| Python | 3.10 | **3.12** |
| GLIBC | 2.35 | **2.39** |
| PostgreSQL (system) | 14 | **16** |
| Redis (system) | 6.0 | **7.0** |
| Node.js (system) | 12.x | **18.x** |

Note: This snap uses `nsg-*` packages and `node/20/stable` snap channel, not system packages directly.

## Recommendation

The migration is **not urgent** — core22 is supported until 2027. The biggest prerequisite is rebuilding all `nsg-*` packages for noble, which is external to this repo. Once that's done, the snap-side changes are a focused 1-2 day effort plus testing. The `snap_daemon` → `_daemon_` UID migration needs careful handling with a data migration hook to avoid breaking existing installs.

## References

- [Snapcraft core22 to core24 migration guide](https://documentation.ubuntu.com/snapcraft/stable/how-to/change-bases/change-from-core22-to-core24/)
- [Migrate to core24 forum thread](https://forum.snapcraft.io/t/migrate-to-core24/39393)
- [System usernames documentation](https://snapcraft.io/docs/system-usernames)
- [snap_daemon deprecation](https://github.com/canonical/snapcraft/issues/5448)
