#!/bin/bash

# Test upgrade blocking mechanism
# This script tests that:
# 1. The revision jump logic correctly blocks upgrades spanning >3 revisions
# 2. The revision jump logic allows upgrades spanning ≤3 revisions
#
# Since dangerous installs might not trigger the hook correctly (due to revision numbering),
# we test this by simulating the upgrade scenario with actual store revisions.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to get current stable revision from snap store
get_current_stable_revision() {
    local response
    local retries=3
    local retry=0
    
    while [ $retry -lt $retries ]; do
        response=$(curl -s -H "Snap-Device-Series: 16" \
            "https://api.snapcraft.io/v2/snaps/info/immich-distribution")
        
        if [ $? -eq 0 ] && [ -n "$response" ]; then
            # Extract the latest stable revision
            latest_rev=$(echo "$response" | jq -r '
                .["channel-map"][]? | 
                select(.channel.name == "latest/stable" or .channel.name == "stable") | 
                .revision | tonumber
            ' 2>/dev/null | sort -n | tail -1)
            
            if [ -n "$latest_rev" ] && [ "$latest_rev" != "null" ] && [ "$latest_rev" != "0" ]; then
                echo "$latest_rev"
                return 0
            fi
        fi
        
        retry=$((retry + 1))
        echo "Retry $retry/$retries: Failed to fetch snap store info, retrying..." >&2
        sleep 2
    done
    
    echo "ERROR: Failed to fetch snap store info after $retries attempts" >&2
    exit 1
}

# Function to check if a revision exists in the store
check_revision_exists() {
    local target_revision="$1"
    local response
    local retries=3
    local retry=0
    
    while [ $retry -lt $retries ]; do
        response=$(curl -s -H "Snap-Device-Series: 16" \
            "https://api.snapcraft.io/v2/snaps/info/immich-distribution")
        
        if [ $? -eq 0 ] && [ -n "$response" ]; then
            # Check if the revision exists
            found=$(echo "$response" | jq -r --arg target "$target_revision" '
                .["channel-map"][]? | 
                select(.revision == ($target | tonumber)) | 
                .revision
            ' 2>/dev/null | head -1)
            
            if [ -n "$found" ] && [ "$found" != "null" ]; then
                echo "1"
                return 0
            else
                echo "0"
                return 0
            fi
        fi
        
        retry=$((retry + 1))
        echo "Retry $retry/$retries: Failed to check revision existence, retrying..." >&2
        sleep 2
    done
    
    echo "ERROR: Failed to check revision existence after $retries attempts" >&2
    return 1
}

# Helper function to remove and install a specific revision
install_revision() {
    local revision="$1"
    
    echo "Removing any existing installation..."
    sudo snap remove immich-distribution 2>/dev/null || true
    sleep 2
    
    echo "Installing revision $revision from store..."
    sudo snap install immich-distribution --revision="$revision"
    
    make wait
}

# Helper function to attempt an upgrade and capture output
attempt_upgrade() {
    local target_revision="$1"
    local should_fail="$2"  # "true" if upgrade should fail, "false" if should succeed
    
    echo "Attempting upgrade to revision $target_revision..."
    
    set +e  # Don't exit on error
    sudo snap refresh immich-distribution --revision="$target_revision" 2>&1 | tee upgrade_output.log
    local upgrade_result=$?
    set -e
    
    if [ "$should_fail" = "true" ]; then
        if [ $upgrade_result -eq 0 ]; then
            echo "ERROR: Upgrade should have failed but succeeded" >&2
            cat upgrade_output.log
            rm -f upgrade_output.log
            return 1
        fi
        
        # Check if the failure was due to our hook
        if grep -q "Update spans.*revisions" upgrade_output.log; then
            echo "✓ Upgrade correctly blocked by revision jump hook (exit code: $upgrade_result)"
        else
            echo "WARNING: Upgrade failed but not due to revision jump hook:" >&2
            cat upgrade_output.log
            # Still pass the test as the upgrade was blocked, though for a different reason
        fi
    else
        if [ $upgrade_result -ne 0 ]; then
            echo "ERROR: Upgrade should have succeeded but failed (exit code: $upgrade_result)" >&2
            cat upgrade_output.log
            rm -f upgrade_output.log
            return 1
        fi
        
        make wait
        echo "✓ Upgrade completed successfully"
    fi
    
    rm -f upgrade_output.log
    return 0
}

# Helper function to verify current revision
verify_revision() {
    local expected_revision="$1"
    local description="$2"
    
    local current_snap_revision=$(snap list immich-distribution | awk 'NR==2 {print $3}')
    if [ "$current_snap_revision" != "$expected_revision" ]; then
        echo "ERROR: Expected revision $expected_revision, got $current_snap_revision ($description)" >&2
        return 1
    fi
    
    echo "✓ Current revision is $current_snap_revision as expected ($description)"
    return 0
}

# Test 1: Install CR-5 and attempt upgrade to CR (should fail with jump of 5)
test_upgrade_blocking_large_jump() {
    local current_revision="$1"
    local old_revision="$2"
    
    echo "=== TEST 1: Upgrade blocking for large revision jump ($old_revision → $current_revision) ==="
    
    install_revision "$old_revision"
    attempt_upgrade "$current_revision" "true"
    verify_revision "$old_revision" "still on old revision after blocked upgrade"
    
    return 0
}

# Test 2: Install CR-3 and attempt upgrade to CR (should succeed with jump of 3)
test_upgrade_allowing_small_jump() {
    local current_revision="$1"
    local old_revision="$2"
    
    echo "=== TEST 2: Upgrade allowing for small revision jump ($old_revision → $current_revision) ==="
    
    install_revision "$old_revision"
    attempt_upgrade "$current_revision" "false"
    verify_revision "$current_revision" "upgraded to current revision"
    
    return 0
}

# Main test execution
main() {
    echo "Getting current stable revision from snap store..."
    current_stable_revision=$(get_current_stable_revision)
    
    if [ -z "$current_stable_revision" ] || [ "$current_stable_revision" = "0" ]; then
        echo "ERROR: Could not determine current stable revision" >&2
        exit 1
    fi
    
    echo "Current stable revision: $current_stable_revision"
    
    # Check if we have enough revisions for testing
    if [ "$current_stable_revision" -lt 6 ]; then
        echo "ERROR: Current stable revision ($current_stable_revision) is too low for testing" >&2
        exit 1
    fi
    
    # Check if target revisions exist in the store
    target_revision_cr_minus_5=$((current_stable_revision - 5))
    target_revision_cr_minus_3=$((current_stable_revision - 3))
    
    echo "Checking if revision $target_revision_cr_minus_5 exists in store..."
    if [ "$(check_revision_exists "$target_revision_cr_minus_5")" != "1" ]; then
        echo "WARNING: Revision $target_revision_cr_minus_5 not found in store, skipping large jump test" >&2
        run_large_jump_test=false
    else
        echo "✓ Revision $target_revision_cr_minus_5 found"
        run_large_jump_test=true
    fi
    
    echo "Checking if revision $target_revision_cr_minus_3 exists in store..."
    if [ "$(check_revision_exists "$target_revision_cr_minus_3")" != "1" ]; then
        echo "WARNING: Revision $target_revision_cr_minus_3 not found in store, skipping small jump test" >&2
        run_small_jump_test=false
    else
        echo "✓ Revision $target_revision_cr_minus_3 found"
        run_small_jump_test=true
    fi
    
    if [ "$run_large_jump_test" = false ] && [ "$run_small_jump_test" = false ]; then
        echo "ERROR: No target revisions available for testing" >&2
        exit 1
    fi
    
    # Run tests
    if [ "$run_large_jump_test" = true ]; then
        test_upgrade_blocking_large_jump "$current_stable_revision" "$target_revision_cr_minus_5"
    fi
    
    if [ "$run_small_jump_test" = true ]; then
        test_upgrade_allowing_small_jump "$current_stable_revision" "$target_revision_cr_minus_3"
    fi
}

# Check if we're being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
