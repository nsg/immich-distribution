# Change Media Location

!!! success "Automatic Legacy Path Migration"
    The Immich Distribution snap automatically detects and fixes legacy media paths during system startup. You will receive notifications in the Immich interface if any migrations are performed or if manual intervention is needed.

## How Automatic Migration Works

The snap includes a background manager that checks your database for legacy media paths during system startup. When detected, it automatically:

1. **Scans** the database for legacy paths from previous installations
2. **Migrates** any found legacy paths to the current media location
3. **Notifies** you of the results through Immich's notification system

### Automatic Detection

The manager automatically checks for and migrates these common legacy paths:

- `upload` (old relative path)
- `/var/snap/immich-distribution/common/data` (incorrect path from improper database migration)
- `/usr/src/app/upload` (Docker container path)
- `/data` (generic Docker path)

### Notifications You May Receive

#### Success Notification

"Media Path Migration Complete" - Database paths have been automatically updated. No action needed.

#### Failure Notification

"Automatic Media Path Migration Failed" - Automatic migration encountered an issue. Manual intervention may be required (see manual instructions below).

!!! info "Notification System"
    The snap uses Immich's built-in notification system to alert admin users. These notifications appear in the Immich web interface and help ensure you're aware of any database path changes.

## Manual Migration (When Needed)

In rare cases where automatic migration fails or you need to migrate custom paths, you can use the manual migration tool.

!!! warning "Backup First"
    Before running this command, ensure you have backups enabled. While the migration is designed to be safe and can be run multiple times, having regular backups ensures you can restore your system if anything unexpected occurs. For detailed backup instructions and options, see the [backup documentation](/configuration/backup-restore/).

Run the change media location command:

```bash
sudo immich-distribution.immich-admin change-media-location
```

!!! note "What to Enter When Prompted"
    When the command asks for paths, you'll need to provide:
    
    - **Previous value**: The old/incorrect path found in your database (e.g., `upload`, `/data`, etc.)
    - **New value**: Always use `/var/snap/immich-distribution/common/upload` for snap installations

### Common Legacy Paths

* Most likely: `upload`
* Less likely: `/var/snap/immich-distribution/common/data`, `/data`, `/usr/src/app/upload`
