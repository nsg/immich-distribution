+++
title = "Immich Admin Extensions"
+++

# Immich Admin Extensions

{% admonition(type="warning", title="Unstable Extension") %}
This is an unstable extension that may disappear at any time. It's not intended for end users to rely on in the long term. When Immich provides an official way to create API keys via CLI, this extension will be removed in favor of the upstream solution.
{% end %}

Immich Distribution extends the upstream `immich-admin` command with additional functionality for automation and server management.

## Create API Key Extension

Create API keys for users directly from the command line:

```bash
# Create an API key with all permissions for admin user
sudo immich-distribution.immich-admin create-api-key

# Create an API key for a specific user by email
sudo immich-distribution.immich-admin create-api-key \
  --name "My API Key" \
  --user-email "user@example.com"

# Create an API key with specific permissions
sudo immich-distribution.immich-admin create-api-key \
  --name "Sync Service Key" \
  --permissions "asset.upload,asset.delete,user.read" \
  --user-email "sync-user@example.com"

# Only create the key if one with the same name doesn't already exist
sudo immich-distribution.immich-admin create-api-key \
  --name "Automation Key" \
  --check
```

### Available Options

- `--name, -n`: Set a custom name for the API key (default: "Admin CLI Key")
- `--permissions, -p`: Specify permissions as comma-separated list, or "all" for full access (default: "all")
- `--user-email, -e`: Create the key for a specific user by email address
- `--user-id, -u`: Create the key for a specific user by ID
- `--check, -c`: Only create the key if one with the same name doesn't already exist
