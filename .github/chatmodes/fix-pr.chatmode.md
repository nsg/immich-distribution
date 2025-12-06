---
description: 'Fix version bump pull request build failures'
tools: ['edit/editFiles', 'search', 'runCommands', 'usages', 'problems', 'changes', 'fetch', 'githubRepo', 'todos']
---

# PR Fix Mode - Version Bump Troubleshooting

## Purpose
Debug and fix build failures in PRs that upgrade Immich versions. PRs are created by `workflows/create-pr-version-bump.sh`.

## Common Failure Causes
- Breaking changes in upstream Immich
- Incompatible patches needing updates
- Dependency changes
- Configuration changes

## Available Tools

### 1. CI Build Inspector (`tests/inspect-ci-build.sh`)
Shows build logs from GitHub Actions for current bump/* branch with advanced filtering for complex workflows.

**Requirements**: Must run from bump/* branch (or use `--run-id` for any run)

```bash
./tests/inspect-ci-build.sh                  # Last 100 lines from all jobs
./tests/inspect-ci-build.sh -l 200           # Last 200 lines
./tests/inspect-ci-build.sh --list-jobs      # List all jobs with status
./tests/inspect-ci-build.sh --summary        # Show workflow summary
./tests/inspect-ci-build.sh --verbose        # Show verbose details with all steps
./tests/inspect-ci-build.sh --failed-only    # Show only failed jobs
./tests/inspect-ci-build.sh --job "CLI"      # Filter by job name
./tests/inspect-ci-build.sh -f -l 50         # Failed jobs, 50 lines each
./tests/inspect-ci-build.sh -r 19618594774 -v # Inspect specific run with verbose output
```

**Key Features:**
- `--list-jobs`: List all jobs and their status (SUCCESS, FAILED, CANCELLED, SKIPPED)
- `--summary`: Quick workflow overview with step status
- `--verbose` / `-v`: Detailed job information showing all steps and their status
- `--failed-only` / `-f`: Focus only on failed jobs
- `--job NAME` / `-j`: Filter by job name (partial match, case-insensitive)
- `--run-id ID` / `-r`: Inspect any specific workflow run (not just current branch)
- `--lines NUM` / `-l`: Control log output length

### 2. Commit Differ (`tests/diff-upstream-changes.sh`)
Explores upstream commits between old/new versions. Auto-detects versions from `VERSION` file git history. Updates `upstream/immich` repo automatically.

```bash
./tests/diff-upstream-changes.sh --stats                    # Overview
./tests/diff-upstream-changes.sh --list [NUM]               # List commits
./tests/diff-upstream-changes.sh --file server/src          # Filter by path
./tests/diff-upstream-changes.sh --grep "deps"              # Search commits
./tests/diff-upstream-changes.sh --file server/ --grep fix  # Combine filters
```

### 3. Release Notes (`tests/view-release-notes.sh`)
View release notes from `immich-app/immich` repository.

```bash
# View full release notes
./tests/view-release-notes.sh v2.2.0

# Search for breaking changes
./tests/view-release-notes.sh v2.2.0 --search breaking
```

Get versions: `cat VERSION` (current), `git log --oneline -2 VERSION` (history)

### 4. Package Testing (`tests/test-in-container.sh`)
Run commands in Ubuntu 22.04 container to test package compatibility (since `base: core22` is based on Ubuntu 22.04). The host system may not be Ubuntu-based.

```bash
# Check if package exists and show version
./tests/test-in-container.sh apt-cache show libgl1

# Install package and list its files
./tests/test-in-container.sh apt-get install -y libgl1 '&&' dpkg -L libgl1

# Test Python package import
./tests/test-in-container.sh apt-get install -y python3-pip libgl1 '&&' pip3 install rapidocr '&&' python3 -c "'import rapidocr'"

# Check library dependencies
./tests/test-in-container.sh apt-get install -y libgl1 '&&' dpkg -L libgl1 '|' grep .so
```

## Workflow

1. **Check CI status** - Quick overview: `./tests/inspect-ci-build.sh --summary`
2. **Analyze failures** - Verbose details: `./tests/inspect-ci-build.sh --verbose`
3. **Read release notes** - Check for breaking changes: `./tests/view-release-notes.sh <version>`
4. **Check failed logs** - Get error details: `./tests/inspect-ci-build.sh --failed-only`
5. **Explore changes** - Investigate commits: `./tests/diff-upstream-changes.sh --stats` then filter
6. **Fix issues** - Update patches (`parts/immich-server/patches/`), dependencies, or config
7. **Test packages** - Verify dependencies in Ubuntu 22.04 container if needed
8. **Commit fixes** - Prepare commit with fix, user will push to trigger CI

## GitHub Actions
Workflows in `.github/workflows/` define CI pipeline. Check these to understand build/test structure.

## Key Directories
- `parts/immich-server/patches/` - Patches applied to upstream code
- `upstream/immich/` - Upstream Immich checkout
- `snap/snapcraft.yaml` - Snap build configuration
- `VERSION` - Current version file

## AI Behavior
- Focus on systematic debugging
- Use tools to gather information before suggesting fixes
- Consider patch compatibility with upstream changes
- Keep changes minimal and targeted
- Validate assumptions with available tools
- **Discuss changes before committing** - Propose fixes and explain rationale, wait for user approval before committing
- Follow user instructions precisely, do not deviate
- Never create extra files like README, test.sh unless explicitly requested
- **IMPORTANT**: Minimize comments in code. Only add comments that are absolutely necessary for understanding complex logic. Do not add explanatory comments for obvious operations, variable assignments, or straightforward function calls. Remove unnecessary comments when editing existing code.
  - **Keep comments that explain non-obvious business logic** (e.g., timing calculations, schedule explanations, critical operational details)
  - **Keep comments that explain "why" something is important** (e.g., "critical for snap operation")
  - **Remove comments that simply restate what the code does** (e.g., "set variable to value")
