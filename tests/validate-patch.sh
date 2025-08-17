#!/bin/bash

# Patch validation script for immich-distribution
# Usage: ./validate-patch.sh <patch_file> <target_file>
# 
# This script validates that a patch can be applied to a target file
# without permanently modifying the upstream repository.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[PATCH VALIDATOR]${NC} ${message}"
}

# Check if required arguments are provided
if [ $# -ne 2 ]; then
    print_status $RED "Usage: $0 <patch_file> <target_file>"
    print_status $YELLOW "Example: $0 parts/immich-server/patches/commands__create-admin-api-key.command.ts.patch upstream/immich/server/src/commands/create-admin-api-key.command.ts"
    exit 1
fi

PATCH_FILE="$1"
TARGET_FILE="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Convert relative paths to absolute paths
if [[ ! "$PATCH_FILE" = /* ]]; then
    PATCH_FILE="$PROJECT_ROOT/$PATCH_FILE"
fi

if [[ ! "$TARGET_FILE" = /* ]]; then
    TARGET_FILE="$PROJECT_ROOT/$TARGET_FILE"
fi

# Validate inputs
if [ ! -f "$PATCH_FILE" ]; then
    print_status $RED "Error: Patch file not found: $PATCH_FILE"
    exit 1
fi

# For new files (when target doesn't exist), check if patch creates the file
if [ ! -f "$TARGET_FILE" ]; then
    print_status $YELLOW "Target file doesn't exist: $TARGET_FILE"
    print_status $BLUE "Checking if patch creates a new file..."
    
    # Check if this is a "new file" patch
    if grep -q "new file mode" "$PATCH_FILE" || grep -q "/dev/null" "$PATCH_FILE"; then
        print_status $GREEN "✓ Patch appears to create a new file"
        
        # Test apply in dry-run mode to validate patch format
        cd "$PROJECT_ROOT/upstream/immich"
        if git apply --check --verbose "$PATCH_FILE" 2>/dev/null; then
            print_status $GREEN "✓ Patch validation successful - creates new file"
            print_status $BLUE "File would be created at: $TARGET_FILE"
            exit 0
        else
            print_status $RED "✗ Patch validation failed - invalid patch format"
            print_status $YELLOW "Attempting to show patch errors:"
            git apply --check --verbose "$PATCH_FILE" 2>&1 || true
            exit 1
        fi
    else
        print_status $RED "Error: Target file doesn't exist and patch doesn't appear to create it"
        exit 1
    fi
fi

print_status $BLUE "Validating patch: $(basename "$PATCH_FILE")"
print_status $BLUE "Target file: $TARGET_FILE"

# Create a temporary backup
BACKUP_FILE="${TARGET_FILE}.backup.$(date +%s)"
cp "$TARGET_FILE" "$BACKUP_FILE"

# Function to cleanup on exit
cleanup() {
    if [ -f "$BACKUP_FILE" ]; then
        print_status $YELLOW "Restoring original file..."
        mv "$BACKUP_FILE" "$TARGET_FILE"
        print_status $BLUE "Original file restored"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Change to the upstream/immich directory for git operations
cd "$PROJECT_ROOT/upstream/immich"

print_status $BLUE "Testing patch application..."

# First, try a dry run to validate the patch
if git apply --check --verbose "$PATCH_FILE" 2>/dev/null; then
    print_status $GREEN "✓ Patch validation successful (dry-run)"
    
    # Now actually apply the patch for full testing
    print_status $BLUE "Applying patch for testing..."
    if git apply "$PATCH_FILE" 2>/dev/null; then
        print_status $GREEN "✓ Patch applied successfully"
        
        # Verify the target file was modified
        if [ -f "$TARGET_FILE" ]; then
            print_status $GREEN "✓ Target file exists after patch application"
            
            # Show a brief diff of what changed
            print_status $BLUE "Changes made to file:"
            echo "---"
            diff -u "$BACKUP_FILE" "$TARGET_FILE" | head -20 || true
            echo "---"
            
        else
            print_status $RED "✗ Target file missing after patch application"
            exit 1
        fi
        
        # Test if we can reverse the patch
        print_status $BLUE "Testing patch reversal..."
        if git apply --reverse "$PATCH_FILE" 2>/dev/null; then
            print_status $GREEN "✓ Patch can be reversed successfully"
            print_status $GREEN "🎉 PATCH VALIDATION COMPLETE - All tests passed!"
        else
            print_status $YELLOW "⚠ Warning: Patch cannot be cleanly reversed"
            print_status $GREEN "✓ But forward application was successful"
        fi
        
    else
        print_status $RED "✗ Failed to apply patch"
        print_status $YELLOW "Error details:"
        git apply "$PATCH_FILE" 2>&1 || true
        exit 1
    fi
    
else
    print_status $RED "✗ Patch validation failed"
    print_status $YELLOW "Error details:"
    git apply --check --verbose "$PATCH_FILE" 2>&1 || true
    exit 1
fi

print_status $GREEN "Patch validation completed successfully!"
