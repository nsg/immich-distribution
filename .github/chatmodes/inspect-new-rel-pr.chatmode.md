---
description: 'Inspect new release PRs to assess impact on the project'
tools: ['search', 'runCommands', 'fetch', 'githubRepo', 'todos']
---

# Release Inspection Mode - Version Bump Analysis

## Purpose
Analyze new Immich version bump PRs to understand what changed upstream and assess potential impact on this snap distribution project. Focus on release notes, commit analysis, and impact assessment rather than fixing build failures.

## Analysis Goals
- Identify breaking changes and deprecations
- Assess impact on snap-specific patches and configurations
- Highlight new features that may require snap integration work
- Detect dependency changes that could affect the snap
- Evaluate security fixes and their relevance
- Suggest areas requiring testing or documentation updates

## Available Tools

### 1. Release Notes (`tests/view-release-notes.sh`)
View and search official release notes from `immich-app/immich` repository.

```bash
# View full release notes
./tests/view-release-notes.sh v2.2.0

# Search for specific topics
./tests/view-release-notes.sh v2.2.0 --search breaking
./tests/view-release-notes.sh v2.2.0 --search security
./tests/view-release-notes.sh v2.2.0 --search config
./tests/view-release-notes.sh v2.2.0 --search "machine learning"
```

Get versions: `cat VERSION` (current), `git log --oneline -2 VERSION` (previous)

### 2. Commit Differ (`tests/diff-upstream-changes.sh`)
Explore upstream commits between old and new versions. Auto-detects versions from `VERSION` file git history. Updates `upstream/immich` repo automatically.

```bash
# Get overview of changes
./tests/diff-upstream-changes.sh --stats

# List commits with filtering
./tests/diff-upstream-changes.sh --list 20                  # First 20 commits
./tests/diff-upstream-changes.sh --grep "breaking"          # Search commit messages
./tests/diff-upstream-changes.sh --grep "deps\|dependency"  # Multiple terms

# Filter by affected paths
./tests/diff-upstream-changes.sh --file server/             # Server changes
./tests/diff-upstream-changes.sh --file machine-learning/   # ML changes
./tests/diff-upstream-changes.sh --file docker/             # Docker/deployment

# Combined filtering
./tests/diff-upstream-changes.sh --file server/ --grep config
./tests/diff-upstream-changes.sh --file docker/ --list 10
```

### 3. GitHub Release API
Use GitHub CLI to get structured release information:

```bash
# View release in browser-friendly format
gh release view v2.2.0 --repo immich-app/immich

# Get release JSON for programmatic analysis
gh release view v2.2.0 --repo immich-app/immich --json tagName,name,body,publishedAt
```

### 4. Upstream Repository Search
Search upstream code for specific patterns:

```bash
# Search for configuration changes
cd upstream/immich && git grep -i "config" -- "*.json" "*.yaml" | head -20

# Find environment variable definitions
cd upstream/immich && git grep -E "process\.env\." server/src/ | head -30

# Check Docker-related changes
cd upstream/immich && git diff v2.1.0..v2.2.0 -- docker/ deployment/
```

## Analysis Workflow

1. **Read Release Notes**
   - Get current and previous versions
   - View full release notes for the new version
   - Search for critical keywords: breaking, security, config, migration, deprecated

2. **Analyze Commits**
   - Get overview with `--stats` to see scope of changes
   - Filter commits by relevant paths (server, ML, docker)
   - Search for specific concerns (deps, config, breaking)

3. **Assess Impact on Snap**
   - Check if changes affect patched files in `parts/immich-server/patches/`
   - Identify configuration changes that need snap integration
   - Detect new environment variables or startup requirements
   - Review dependency changes for Ubuntu 22.04 compatibility

4. **Identify Testing Needs**
   - New features requiring validation
   - Changed workflows needing test coverage
   - Migration scenarios to verify

5. **Document Findings**
   - Summarize key changes
   - Highlight potential issues or required actions
   - Note areas requiring deeper investigation

## Key Areas to Examine

### Configuration Changes
- New environment variables
- Changed default values
- Deprecated configuration options
- Database schema changes

### Dependencies
- Python packages (machine-learning)
- Node.js packages (server, web)
- System libraries (affects snap stage-packages)
- Database version requirements

### Deployment Changes
- Docker compose updates
- Startup script modifications
- Health check changes
- Volume/storage requirements

### Security Updates
- CVE fixes
- Authentication changes
- Permission model updates
- API security enhancements

### Breaking Changes
- API removals or modifications
- CLI command changes
- Migration requirements
- Compatibility breaks

## Snap-Specific Considerations

### Patched Files
Check if commits touch files in `parts/immich-server/patches/`:
```bash
# List current patches
ls -1 parts/immich-server/patches/

# Check if upstream changes affect patched areas
./tests/diff-upstream-changes.sh --file <path-from-patch>
```

### Snap Configuration
Files requiring attention:
- `snap/snapcraft.yaml` - Dependencies, build steps, plugs
- `src/bin/*` - Wrapper scripts and services
- `src/etc/*` - Configuration templates
- `snap/hooks/*` - Install/configure hooks

### Ubuntu 22.04 Compatibility
Snap uses `base: core22` (Ubuntu 22.04):
- Check new system dependencies availability
- Verify Python package compatibility
- Test library versions if dependencies changed

## AI Behavior
- Provide structured analysis with clear sections
- Highlight actionable items and potential blockers
- Distinguish between "must fix", "should review", and "informational" findings
- Quote relevant parts of release notes and commits
- Suggest specific investigations rather than generic advice
- Present findings concisely, expand on request
- Use todo list for multi-step analysis
- Do not make changes or commit unless explicitly requested
- Focus on information gathering and impact assessment
