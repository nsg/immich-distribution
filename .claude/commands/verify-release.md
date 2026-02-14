---
description: Verify upstream release impact on snap package
model: opus
allowed-tools: Read, Grep, Glob, Bash(git:*), Bash(gh:*), Bash(cat:*), Bash(unzip:*), Bash(ls:*), Bash(wc:*), Task, WebFetch
---

You are verifying an upstream Immich release for the snap distribution package. Follow each phase below. Use subagents aggressively for parallel work.

## Setup

Determine versions and PR:
```bash
CURRENT=$(cat VERSION | tr -d '[:space:]')
PREVIOUS=$(git show $(git log --oneline -2 VERSION | tail -1 | cut -d' ' -f1):VERSION | tr -d '[:space:]')
BRANCH=$(git branch --show-current)
PR_NUMBER=$(gh pr list --head "$BRANCH" --json number --jq '.[0].number')
```

Store these for use throughout. Fetch the full PR body with `gh pr view $PR_NUMBER --json body --jq .body`.

**Compute all intermediate versions** between PREVIOUS and CURRENT. If multiple patch releases were skipped (e.g. PREVIOUS=1.5.0 and CURRENT=1.5.6), we need release notes for every version in between. Enumerate them:
```bash
# Given PREVIOUS and CURRENT share major.minor, enumerate all patch versions
MAJOR_MINOR=$(echo $CURRENT | cut -d. -f1-2)
PREV_PATCH=$(echo $PREVIOUS | cut -d. -f3)
CURR_PATCH=$(echo $CURRENT | cut -d. -f3)
ALL_VERSIONS=""
for p in $(seq $((PREV_PATCH + 1)) $CURR_PATCH); do
  ALL_VERSIONS="$ALL_VERSIONS $MAJOR_MINOR.$p"
done
echo "Versions to check: $ALL_VERSIONS"
```

If major or minor versions differ, use `gh release list --repo immich-app/immich --limit 50` to find all releases between PREVIOUS and CURRENT instead of the patch enumeration above.

Store ALL_VERSIONS for Subagent A.

Ensure the upstream repo is available and fetch tags:
```bash
cd upstream/immich && git fetch --tags --quiet origin && cd -
```

Get ALL commits between the two versions:
```bash
cd upstream/immich && git log --oneline --no-merges v$PREVIOUS..v$CURRENT && cd -
```

Also read our current patches to know which files they target:
```bash
ls -1 parts/immich-server/patches/
```

## Phase 1 & 2: Release Notes + Commit Analysis (parallel)

Launch these two subagents **in parallel** — they are independent of each other.

### Subagent A: Upstream Release Notes Analysis

We may have skipped multiple upstream releases. ALL_VERSIONS (computed in Setup) contains every version between PREVIOUS and CURRENT that needs its release notes checked.

Launch a **single subagent** (Task tool, subagent_type: general-purpose, model: sonnet) with ALL_VERSIONS. The subagent must:

- For **each version** in ALL_VERSIONS, fetch release notes using `gh release view v<version> --repo immich-app/immich --json body --jq .body`. If a release doesn't exist for a particular version, note it and move on.
- Also extract any upstream release notes URLs from the PR body (under "## Upstream release notes") and fetch those with WebFetch for additional context
- Analyze **all** release notes collectively for changes that affect this snap package, considering:
  - Database schema changes (affects `src/etc/modify-db.sql` custom tables/triggers on `asset` table)
  - Dependency version bumps (Node.js, Python, Redis, PostgreSQL, libvips, Sharp, ffmpeg, onnxruntime)
  - New environment variables or config changes (we map these via `snap set/get`)
  - API changes that affect our patches in `parts/immich-server/patches/`
  - Machine learning model or runtime changes (we're CPU-only, no CUDA)
  - File path changes (snap layouts have hardcoded paths)
  - Breaking changes listed explicitly — but remember: Docker-specific breaking changes may NOT affect us, and unlisted changes MAY affect us
- Return a structured summary of findings relevant to this snap package, **noting which version each finding comes from**

### Subagent B: Commit-Level Analysis (coordinator)

Launch a **single coordinator subagent** (Task tool, subagent_type: general-purpose, model: sonnet) that will handle the entire commit analysis internally. Pass it:

- The full commit list (from `git log` above)
- The list of patch files and their target paths
- The PREVIOUS and CURRENT version strings
- The working directory path for `upstream/immich`

The coordinator subagent must:

1. **Discover the repository structure** by listing top-level directories in the upstream repo (`ls upstream/immich/`). Decide which paths are relevant to a snap server/ML package and which are not (e.g. web UI, mobile app, docs that aren't env-var docs, GitHub workflows, etc. are typically irrelevant). Use this to build a path exclusion list.
2. **Pre-filter commits** using `git log --oneline --no-merges v$PREVIOUS..v$CURRENT -- <relevant-paths>` to get only commits touching relevant paths. Also separately check root-level config files like `docker-compose.yml`, `Dockerfile`s, `package.json`, `pyproject.toml`. Log how many commits were filtered out.
3. **Split the filtered commits** into **10 roughly equal batches** (or fewer if there aren't enough commits)
4. **Launch workers in parallel** (Task tool, subagent_type: general-purpose, model: haiku), each receiving its batch of commit hashes with instructions to:
   - First run `git show <hash> --stat` to see which files changed
   - Only fetch full diffs (`git show <hash> -- <file>`) for files that look relevant to the snap package
   - Watch for:
     - Changes to files our patches touch
     - Database migrations or schema changes (especially the `asset` table)
     - Dependency version changes in `package.json`, `pyproject.toml`, `Dockerfile`s
     - New or changed environment variables
     - Changes to server startup, CLI commands, or service architecture
     - Path changes that would break snap layouts
     - Sharp/libvips related changes
     - Machine learning model loading or runtime changes
     - Changes to `extism-js` or plugin system
     - PostgreSQL, Redis, or other infrastructure changes
     - Python version requirement changes (we're pinned to 3.10 via core22)
     - Node.js version requirement changes (we use node/20/stable snap)
   - Return: for each commit with relevant findings, the hash, one-line summary, and what specifically is relevant
5. After all workers complete, **collate findings, discard commits with no findings**, and return a concise aggregated summary grouped by category

This two-tier approach keeps the main context clean — only the coordinator's aggregated result comes back.

## Phase 3: CI Status Check

Check CI status:
```bash
BRANCH=$(git branch --show-current)
RUN_ID=$(gh run list --branch "$BRANCH" --limit 1 --json databaseId --jq '.[0].databaseId')
gh run view $RUN_ID --json jobs --jq '.jobs[] | "[\(.conclusion // "running" | ascii_upcase)] \(.name)"'
```

If ALL jobs passed: report success briefly.

If any jobs FAILED: download and inspect logs using subagents:
```bash
gh ext run-logs $RUN_ID
```
This outputs a zip file path. Unzip it and use **one subagent per failed job** (Task tool, subagent_type: general-purpose) to:
- Read the relevant log file
- Identify the root cause of the failure
- Search upstream GitHub issues if the failure seems related to upstream changes: `gh search issues --repo immich-app/immich "<search terms>"`
- Suggest fixes specific to this snap package

If CI is still running: report that and show which jobs are in progress.

## Phase 4: Summary Report

Present a clear, concise summary with sections:

1. **Release Overview** — Version bump, one-line summary
2. **Release Notes Findings** — What from the release notes affects us
3. **Commit Analysis Findings** — Commits that need attention, grouped by category
4. **CI Status** — Pass/fail, failures explained
5. **Action Items** — Numbered list of concrete things to do before merging (patches to update, configs to change, versions to bump, etc.)

Be critical and specific. Don't just list things — state whether they actually affect us and why. Docker-specific changes often don't matter for a snap package. But Python version bumps, schema changes, and dependency shifts definitely do.
