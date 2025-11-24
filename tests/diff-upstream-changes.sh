#!/bin/bash
set -e

UPSTREAM_DIR="upstream/immich"
VERSION_FILE="VERSION"

function show_help {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Explore changes in upstream Immich between version bumps.

OPTIONS:
    -s, --stats         Show change statistics by directory
    -l, --list [NUM]    List commits (default: 20, use 'all' for all commits)
    -f, --file PATH     Show commits that changed a specific file/directory
    -a, --author NAME   Filter commits by author
    -g, --grep TEXT     Search commit messages
    -h, --help          Show this help message

EXAMPLES:
    # Show statistics of changes by directory
    $(basename "$0") --stats

    # List last 20 commits
    $(basename "$0") --list

    # List all commits
    $(basename "$0") --list all

    # Show commits that changed server code
    $(basename "$0") --file server/

    # Search for dependency-related commits
    $(basename "$0") --grep "dep"

    # Combine filters
    $(basename "$0") --file server/src --grep "fix"
EOF
}

# Get current and previous version
function get_versions {
    CURRENT_VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')
    
    # Get the previous commit that modified VERSION
    PREV_COMMIT=$(git log --oneline -2 "$VERSION_FILE" | tail -1 | cut -d' ' -f1)
    PREVIOUS_VERSION=$(git show "$PREV_COMMIT:$VERSION_FILE" | tr -d '[:space:]')
    
    echo "Comparing upstream changes:"
    echo "  Previous: $PREVIOUS_VERSION"
    echo "  Current:  $CURRENT_VERSION"
    echo ""
}

# Update upstream repository
function update_upstream {
    if [ ! -d "$UPSTREAM_DIR" ]; then
        echo "Error: Upstream directory not found: $UPSTREAM_DIR"
        exit 1
    fi
    
    echo "Updating upstream repository..."
    cd "$UPSTREAM_DIR"
    git fetch --tags --quiet origin
    cd - > /dev/null
    echo ""
}

# Show statistics
function show_stats {
    get_versions
    update_upstream
    
    cd "$UPSTREAM_DIR"
    
    TOTAL=$(git log --oneline "$PREVIOUS_VERSION..$CURRENT_VERSION" | wc -l)
    echo "Total commits: $TOTAL"
    echo ""
    
    echo "=== Changes by Directory ==="
    git diff --stat "$PREVIOUS_VERSION..$CURRENT_VERSION" | tail -1
    echo ""
    git diff --dirstat=files,10 "$PREVIOUS_VERSION..$CURRENT_VERSION" | head -20
    
    echo ""
    echo "=== Top Changed Files ==="
    git log --pretty=format: --name-only "$PREVIOUS_VERSION..$CURRENT_VERSION" | sort | uniq -c | sort -rn | head -20
    
    cd - > /dev/null
}

# List commits
function list_commits {
    local limit=$1
    get_versions
    update_upstream
    
    cd "$UPSTREAM_DIR"
    
    local git_opts="--oneline --no-merges"
    local git_range="$PREVIOUS_VERSION..$CURRENT_VERSION"
    
    if [ -n "$AUTHOR_FILTER" ]; then
        git_opts="$git_opts --author=$AUTHOR_FILTER"
    fi
    
    if [ -n "$GREP_FILTER" ]; then
        git_opts="$git_opts --grep=\"$GREP_FILTER\""
    fi
    
    local cmd="git log $git_opts $git_range"
    
    if [ -n "$FILE_FILTER" ]; then
        cmd="$cmd -- $FILE_FILTER"
    fi
    
    if [ "$limit" = "all" ]; then
        eval "$cmd"
    else
        local count=$(eval "$cmd" | wc -l)
        echo "Showing $limit of $count commits"
        echo ""
        eval "$cmd" | head -n "$limit"
        
        if [ "$limit" -lt "$count" ]; then
            echo ""
            echo "... $(($count - $limit)) more commits. Use --list all to see all."
        fi
    fi
    
    cd - > /dev/null
}

# Parse arguments
COMMAND=""
LIST_LIMIT=20
FILE_FILTER=""
AUTHOR_FILTER=""
GREP_FILTER=""

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stats)
            COMMAND="stats"
            shift
            ;;
        -l|--list)
            COMMAND="list"
            if [ -n "$2" ] && [[ "$2" != -* ]]; then
                LIST_LIMIT="$2"
                shift
            fi
            shift
            ;;
        -f|--file)
            FILE_FILTER="$2"
            shift 2
            ;;
        -a|--author)
            AUTHOR_FILTER="$2"
            shift 2
            ;;
        -g|--grep)
            GREP_FILTER="$2"
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

# Execute command
case "$COMMAND" in
    stats)
        show_stats
        ;;
    list)
        list_commits "$LIST_LIMIT"
        ;;
    *)
        show_help
        exit 1
        ;;
esac
