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

new_cli_version() {
    latest_immich_cli_version=$(curl -s https://api.github.com/repos/immich-app/CLI/releases/latest | jq -r '.tag_name')
    if grep -q $latest_immich_cli_version snap/snapcraft.yaml; then
        echo "No new immich-cli version available."
    else
        echo "Note, new immich-cli version available: $latest_immich_cli_version"
    fi
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
    curl -s https://api.github.com/repos/immich-app/immich/releases/latest | jq -r '.tag_name'
}

get_latest_releases() {
    curl -s https://api.github.com/repos/immich-app/immich/releases | jq -r '.[].tag_name'
}

get_latest_release_for_major_minor() {
    local major_minor="$1"

    get_latest_releases | grep "^$major_minor" | sort -V | tail -n1
}

snapstore_version() {
    snap info immich-distribution | awk "/^ *latest\/$1/{ print \$2 }" | cut -d'-' -f1
}
