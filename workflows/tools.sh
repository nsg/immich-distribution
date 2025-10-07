#
# These functions are included by other scripts in the workflows directory.
#

get_issue_number() {
    gh issue list \
        --label new-version \
        --state open \
        --search "Immich $1 released" \
        --json number \
        --limit 1 \
        --jq ".[].number" 2>/dev/null
}

get_issue_body() {
    gh issue view $1 --json body --jq ".body"
}

get_issue_title() {
    gh issue view $1 --json title --jq ".title"
}

list_tracking_issues() {
    gh issue list \
        --label new-version \
        --state open \
        --search "Immich released" \
        --json number \
        --jq ".[].number" 2>/dev/null
}

get_pr_number() {
    gh pr list \
        --state open \
        --search "Bump $1" \
        --json number \
        --limit 1 \
        --jq ".[].number" 2>/dev/null
}

has_any_pr_bump_open() {
    get_pr_number | grep -qE '.'
}

create_pr() {
    gh pr create --base master --assignee=nsg --title "Bump $NEW_VERSION" --body-file -
}

create_issue() {
    local new_version="$1"
    local new_version_major_minor=$(echo $new_version | cut -d. -f1-2)

    gh issue create --title "Immich $new_version_major_minor released" --label new-version --body-file -
}

create_issue_body() {
    local new_version="$1"
    local new_version_major_minor=$(echo $new_version | cut -d. -f1-2)

    NEW_VERSION="$new_version" \
        NEW_VERSION_MAJOR_MINOR="$new_version_major_minor" \
        envsubst < workflows/issue-template.md
}

has_version_tracking_issue() {
    local new_version="$1"
    local new_version_major_minor=$(echo $new_version | cut -d. -f1-2)

    get_issue_number "$new_version_major_minor" | grep -qE '.'
}

get_latest_release() {
    local retries=10
    local delay=2
    local result
    
    for i in $(seq 1 $retries); do
        result=$(curl -s https://api.github.com/repos/immich-app/immich/releases/latest | jq -r '.tag_name')
        
        if [ -n "$result" ] && [ "$result" != "null" ]; then
            echo "$result"
            return 0
        fi
        
        echo "Attempt $i failed, retrying in $delay seconds..." >&2
        sleep $delay
    done
    
    echo "$result"
}

get_latest_releases() {
    local retries=10
    local delay=2
    local result
    
    for i in $(seq 1 $retries); do
        result=$(curl -s https://api.github.com/repos/immich-app/immich/releases | jq -r '.[].tag_name')
        
        if [ -n "$result" ] && [ "$result" != "null" ]; then
            echo "$result"
            return 0
        fi
        
        echo "Attempt $i failed, retrying in $delay seconds..." >&2
        sleep $delay
    done
    
    echo "$result"
}

get_latest_release_for_major_minor() {
    local major_minor="$1"

    get_latest_releases | grep "^$major_minor" | sort -V | tail -n1
}

snapstore_version() {
    local retries=20
    local delay=2
    local result
    
    for i in $(seq 1 $retries); do
        result=$(snap info immich-distribution 2>/dev/null | awk "/^ *latest\/$1/{ print \$2 }" | cut -d'-' -f1)
        
        if [ -n "$result" ] && [[ "$result" != *"error"* ]]; then
            echo "$result"
            return 0
        fi
        
        if [ $i -lt $retries ]; then
            echo "Attempt $i failed, retrying in $delay seconds..." >&2
            sleep $delay
            delay=$((delay * 2))
        fi
    done
    
    echo "$result"
}

version_to_int() {
    echo $1 | sed 's/^v//' | awk -F'.' '{ print $1*1000000 + $2*1000 + $3 }'
}
