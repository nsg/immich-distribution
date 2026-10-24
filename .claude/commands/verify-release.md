---
description: Verify upstream release impact on snap package
allowed-tools: Read, Grep, Glob, Bash(git:*), Bash(gh:*), Bash(cat:*), Bash(unzip:*), Bash(ls:*), Bash(wc:*), Bash(curl:*), Bash(/usr/bin/ssh:*), Bash(/usr/bin/scp:*), Bash(rsync:*), Task, WebFetch, Skill, mcp__playwright
---

Verify the upstream Immich release this bump branch targets: analyze everything between PREVIOUS and CURRENT, then report findings and action items.

**Verification only — the repository stays read-only.** Never modify this repository or write fixes/news entries; every problem becomes an action item. Building on the build host, deploying to Telesnap and keeping scratch output under `.claude-sandbox/` are allowed (section 7).

Bump workflow: one tracking issue per minor (1.x), one PR per patch (1.2.x); CI runs extensive tests on `bump/*` branches. The PR for this branch has a body containing upstream release notes URLs and **monitored upstream file diffs** — pre-selected high-risk files. Analyze those diffs, don't skip them. An "Error, \<file\> do not exists" line means upstream moved/deleted a monitored file — find where it went and whether we still reference the old path.

Fan out subagents for the independent analyses below and keep raw diffs/logs out of the main context. Don't use more smarts than a task needs: run mechanical checks (patch `git apply --check`, path/version-string existence, CI log retrieval) on `model: haiku`, and reserve the default session model for analysis-heavy work (release notes, schema/commit review, dependency comparison). The AGENTS.md gotchas are the review checklist — pass the relevant ones to each subagent. Be critical: Docker-specific breaking changes often don't affect a snap package; schema changes, dependency shifts, and Python/Node requirement changes definitely do.

## Inputs

- CURRENT is in `VERSION`; PREVIOUS is the file's content before the last commit that changed it.
- Check release notes for **every** upstream release between PREVIOUS and CURRENT, not just the latest. For major bumps, also find the upstream migration guide / breaking-changes post.

## What to verify

1. **Release notes + monitored diffs** — anything that hits an AGENTS.md gotcha: schema changes, dependency bumps, new/changed env vars, path restructuring, ML runtime changes.
2. **Commit sweep** — commits in `upstream/immich` between the two tags, analyzing full diffs, not just messages. Path-filter to server, machine-learning, packages, migrations, Dockerfiles, and root config (web UI, mobile, and non-env-var docs usually don't matter); exclude lockfiles and generated files from diffs. Chunk across `model: sonnet` subagents for routine patch bumps; use `model: opus` when the range is high-risk — a major version bump, hundreds of commits, or known schema/dependency breaks. Each agent needs two things to judge "will this affect the snap package": the AGENTS.md overview and gotchas, and a short description of what we ship and add on top (the parts and build steps in `snap/snapcraft.yaml`, the patches in `parts/immich-server/patches/`, config hooks) — so it can reason from what the package contains, not only pattern-match the gotcha list. Tell agents to over-flag: report anything plausibly relevant with a one-line reason. Review the flagged commits yourself.
3. **Base images & `nsg-*` packages** — if the `base-server-*` tags in `server/Dockerfile` changed, review what changed in `immich-app/base-images` between those dates and compare each mirrored dependency against the version we publish in `upstream/aptly` (pull it first; on failure fall back to `tests/test_vips_version.py`). A mismatch means an APT package bump (blocks the snap build — flag prominently) and possibly a hardcoded layout version in `snap/snapcraft.yaml`.
4. **Patches** — check out `v$CURRENT` in `upstream/immich` and `git apply --check -p1` each patch in `parts/immich-server/patches/`. For any that break, find out what happened to the target file.
5. **Snapcraft vs upstream tree** — paths and version strings that `snap/snapcraft.yaml` build steps reference in the upstream tree (plugins part, `mise.toml` locations, sed/grep targets like the extism-js pin) must still exist and match at `v$CURRENT`.
6. **CI** — latest run on this branch, one subagent per failed job. When a failure looks upstream-caused, search upstream issues and check the other `immich-app` org repos we depend on.
7. **Deployment testing (judgment call)** — CI only exercises fresh installs and backup/restore; it never refreshes a populated store revision in place. Deploy to Telesnap when sections 1–6 leave runtime questions open: migrations (above all on populated tables), runtime/dependency shifts (Node, Python, `nsg-*`, ffmpeg), changed hooks or config, or a suspicious upstream change you want to see working. For a trivial bump with green CI, skip it and say why. Follow `SNAPTEST.md` and the AGENTS.md *Building*, *Test Installation*, *Test Isolation* and *Exploratory Browser Testing* rules.
   - **New snap** — build it from the bump branch with the `build-host` skill and copy it back (CI artifacts are out of reach: the sandbox's `gh` proxy rejects `gh run download`). Start the build early, while the old revision is being populated.
   - **Upgrade** — get the revision users run now (stable, plus beta/edge if they differ) from the Snap Store API (`api.snapcraft.io/v2/snaps/info/immich-distribution`, header `Snap-Device-Series: 16`, download URL in the channel map) — Telesnap installs only uploaded files. Install it, run `tests/test_prep.py`, populate data that the changes touch (e.g. people assets for face/person migrations), then upload the new snap to the Telesnap upgrade endpoint. Check that refresh hooks pass, migrations run (and how long they take), services come up, and data survives.
   - **Fresh install** — purge, install the new snap alone, and compare against the upgraded instance when the upgrade looked off.
   - **Explore** — read logs through the Telesnap logs endpoint and click through the affected UI paths with the Playwright MCP, watching console and network errors. Save screenshots under `.claude-sandbox/verify-v$CURRENT/` and show anything wrong to the user.

   Only one installation per snap name exists on Telesnap: purge between scenarios. Run deploy steps from a single agent and keep raw logs out of the main context.

## Report

Concise summary grouped by the areas above, then numbered action items stating what must happen before merge. For deployment testing, state which scenarios ran (old → new revision, fresh) and what they showed, or why you skipped them. Two questions must be answered explicitly, even if the answer is "not needed":

- **Era bump** — should `IMMICH_DISTRIBUTION_ERA` be incremented (major version or destructive schema change on tables our custom SQL touches), so users can't skip over this version? Recommend with reasoning.
- **News entry** — recommend one if the release has user-visible impact (`docs/site/content/news/YYYY/MM/DD-slug.md`, see recent entries for format). Outline its content; don't write it.
