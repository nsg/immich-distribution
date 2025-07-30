---
date: 2025-07-30
authors: [nsg]
---

# Automatic API Key for System Administration

Starting with revision 213, Immich Distribution automatically creates an internal API key for system administration tasks. This change has been in beta and is now released to stable.

## What's New

The manager service automatically creates an API key named `immich-distribution` for the first admin user. This key is used exclusively for internal operations and enables the system to use official Immich APIs instead of direct database access for automated tasks.

## What You Need to Know

- **No action required** - The key is created and managed automatically
- **Internal use only** - Not accessible to users, only for system operations
- **Maintenance schedule** - Checked and recreated if needed twice daily (06:00 and 18:00)

This change improves reliability and follows best practices by using official APIs over custom solutions for internal functionality, internal scripts, and internal processes.

We have also extended the immich-admin CLI command with an extension to allow us to create this API key from inside the snap package. For more information about this extension, see the [Immich Admin Extensions](/configuration/cli-administration/) documentation.

If you notice any unexpected behavior, please report it on the [GitHub repository](https://github.com/nsg/immich-distribution/issues).
