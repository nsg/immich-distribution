#!/bin/bash
set -e

REPO="nsg/immich-distribution"
NUM_LINES=100
FAILED_ONLY=false
JOB_FILTER=""
LIST_JOBS=false
SHOW_SUMMARY=false
SHOW_VERBOSE=false
SPECIFIC_RUN_ID=""

function show_help {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Inspect CI build logs for bump/* branches.

OPTIONS:
    -l, --lines NUM     Number of lines to show (default: 100)
    -j, --job NAME      Filter logs by job name (partial match)
    -f, --failed-only   Show only failed jobs
    --list-jobs         List all jobs and exit
    -s, --summary       Show workflow summary with step details
    -v, --verbose       Show verbose job details with steps
    -r, --run-id ID     Inspect specific run ID instead of latest
    -h, --help          Show this help message

EXAMPLES:
    # Show last 100 lines (default)
    $(basename "$0")

    # Show last 200 lines
    $(basename "$0") --lines 200

    # List all jobs with their status
    $(basename "$0") --list-jobs

    # Show workflow summary with step details
    $(basename "$0") --summary

    # Show verbose job details with all steps
    $(basename "$0") --verbose

    # Show logs only for failed jobs
    $(basename "$0") --failed-only

    # Show logs for specific job (partial name match)
    $(basename "$0") --job "Test CLI"
    $(basename "$0") --job "assets"

    # Inspect a specific run ID
    $(basename "$0") --run-id 19618594774 --verbose

    # Combine filters
    $(basename "$0") --failed-only --lines 50
EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--lines)
            NUM_LINES="$2"
            shift 2
            ;;
        -j|--job)
            JOB_FILTER="$2"
            shift 2
            ;;
        -f|--failed-only)
            FAILED_ONLY=true
            shift
            ;;
        --list-jobs)
            LIST_JOBS=true
            shift
            ;;
        -s|--summary)
            SHOW_SUMMARY=true
            shift
            ;;
        -v|--verbose)
            SHOW_VERBOSE=true
            shift
            ;;
        -r|--run-id)
            SPECIFIC_RUN_ID="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

if ! gh auth status &>/dev/null; then
    echo "Error: Not authenticated with GitHub CLI"
    echo "Please run: gh auth login"
    exit 1
fi

if [ -z "$SPECIFIC_RUN_ID" ]; then
    BRANCH=$(git branch --show-current)

    if [[ ! "$BRANCH" =~ ^bump/ ]]; then
        echo "Error: Current branch '$BRANCH' does not start with 'bump/'"
        echo "This script is designed to inspect CI builds for version bump branches"
        echo "Use --run-id to specify a specific run ID to inspect"
        exit 1
    fi

    echo "Inspecting CI builds for branch: $BRANCH"
    echo "Repository: $REPO"
    echo ""

    echo "Fetching latest workflow runs..."
    RUN_ID=$(gh run list --repo "$REPO" --branch "$BRANCH" --limit 1 --json databaseId --jq '.[0].databaseId')

    if [ -z "$RUN_ID" ]; then
        echo "Error: No workflow runs found for branch $BRANCH"
        exit 1
    fi
else
    RUN_ID="$SPECIFIC_RUN_ID"
    echo "Inspecting specific run ID: $RUN_ID"
    echo "Repository: $REPO"
    echo ""
fi

echo "Latest run ID: $RUN_ID"
echo ""

if [ "$SHOW_VERBOSE" = true ]; then
    echo "=== Verbose Workflow Details ==="
    gh run view "$RUN_ID" --repo "$REPO" -v
    exit 0
fi

if [ "$SHOW_SUMMARY" = true ]; then
    echo "=== Workflow Summary ==="
    gh run view "$RUN_ID" --repo "$REPO"
    exit 0
fi

JOBS_JSON=$(gh run view "$RUN_ID" --repo "$REPO" --json jobs --jq '.jobs')

if [ "$LIST_JOBS" = true ]; then
    echo "=== Jobs in this workflow run ==="
    echo ""
    echo "$JOBS_JSON" | jq -r '.[] | "[\(.conclusion // "running" | ascii_upcase)] \(.name) (ID: \(.databaseId))"'
    exit 0
fi

echo "=== Workflow Run Details ==="
gh run view "$RUN_ID" --repo "$REPO"

echo ""
echo "=== Jobs Summary ==="
echo "$JOBS_JSON" | jq -r '.[] | "[\(.conclusion // "running" | ascii_upcase)] \(.name)"'
echo ""

FAILED_JOB_IDS=()
if [ "$FAILED_ONLY" = true ]; then
    readarray -t FAILED_JOB_IDS < <(echo "$JOBS_JSON" | jq -r '.[] | select(.conclusion == "failure") | .databaseId')
    if [ ${#FAILED_JOB_IDS[@]} -eq 0 ]; then
        echo "No failed jobs found"
        exit 0
    fi
    echo "Found ${#FAILED_JOB_IDS[@]} failed job(s)"
fi

FILTERED_JOB_IDS=()
if [ -n "$JOB_FILTER" ]; then
    readarray -t FILTERED_JOB_IDS < <(echo "$JOBS_JSON" | jq -r --arg filter "$JOB_FILTER" '.[] | select(.name | test($filter; "i")) | .databaseId')
    if [ ${#FILTERED_JOB_IDS[@]} -eq 0 ]; then
        echo "No jobs found matching filter: $JOB_FILTER"
        exit 1
    fi
    echo "Found ${#FILTERED_JOB_IDS[@]} job(s) matching filter: $JOB_FILTER"
fi

echo ""
echo "=== Build Logs (last $NUM_LINES lines) ==="
echo ""

if [ "$FAILED_ONLY" = true ]; then
    for job_id in "${FAILED_JOB_IDS[@]}"; do
        JOB_NAME=$(echo "$JOBS_JSON" | jq -r --arg id "$job_id" '.[] | select(.databaseId == ($id | tonumber)) | .name')
        echo "=========================================="
        echo "Job: $JOB_NAME (ID: $job_id)"
        echo "=========================================="
        gh run view "$RUN_ID" --repo "$REPO" --log | grep -A 999999 "^$JOB_NAME" | head -n "$NUM_LINES" || true
        echo ""
    done
elif [ -n "$JOB_FILTER" ]; then
    for job_id in "${FILTERED_JOB_IDS[@]}"; do
        JOB_NAME=$(echo "$JOBS_JSON" | jq -r --arg id "$job_id" '.[] | select(.databaseId == ($id | tonumber)) | .name')
        echo "=========================================="
        echo "Job: $JOB_NAME (ID: $job_id)"
        echo "=========================================="
        gh run view "$RUN_ID" --repo "$REPO" --log | grep -A 999999 "^$JOB_NAME" | head -n "$NUM_LINES" || true
        echo ""
    done
else
    gh run view "$RUN_ID" --repo "$REPO" --log | tail -n "$NUM_LINES"
fi

echo ""
echo "=== Summary ==="
if [ "$FAILED_ONLY" = true ]; then
    echo "Showed logs from ${#FAILED_JOB_IDS[@]} failed job(s)"
elif [ -n "$JOB_FILTER" ]; then
    echo "Showed logs from ${#FILTERED_JOB_IDS[@]} job(s) matching: $JOB_FILTER"
else
    echo "Showing last $NUM_LINES lines from all jobs"
fi
echo "Use --lines NUM to adjust line count"
echo "Use --list-jobs to see all jobs"
echo "Use --failed-only to show only failed jobs"
echo "Use --job NAME to filter by job name"
echo ""
echo "To view this run in browser:"
gh run view "$RUN_ID" --repo "$REPO" --web --exit-status || echo "https://github.com/$REPO/actions/runs/$RUN_ID"
