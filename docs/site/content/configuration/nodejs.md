+++
title = "Node.js Options"
+++

# Node.js Options

Configure Node.js command-line options for the Immich server using the `NODE_OPTIONS` environment variable. This allows you to customize Node.js behavior, memory limits, garbage collection, and other runtime settings.

## Configuration

```bash
# Set maximum heap size to 4GB
sudo snap set immich-distribution node-options="--max-old-space-size=4096"

# Multiple options (space-separated)
sudo snap set immich-distribution node-options="--max-old-space-size=8192 --max-semi-space-size=128"

# Reset to default
sudo snap set immich-distribution node-options=""

# Check current setting
sudo snap get immich-distribution node-options
```

The immich-server service restarts automatically when you change the configuration.

## Example: Fixing Memory Errors

If you encounter "JavaScript heap out of memory" errors with large photo libraries (as reported in [issue #256](https://github.com/nsg/immich-distribution/issues/256)):

```bash
# Set heap size to 8GB
sudo snap set immich-distribution node-options="--max-old-space-size=8192"
```

For more NODE_OPTIONS configuration options, see the [Node.js CLI documentation](https://nodejs.org/api/cli.html).
