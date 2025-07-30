# Notification System

The notification system allows you to send system notifications to Immich users through the admin API. This is useful for automation scripts, backup notifications, and system maintenance alerts.

## Usage

```bash
sudo immich-distribution.notification -t "Notification Title" [options]
```

### Required Parameters

- `-t title`: The title of the notification (required)

### Optional Parameters

- `-u userId`: Send notification to a specific user ID (if omitted, sends to all admin users)
- `-l level`: Set the notification level (`success`, `error`, `warning`, `info`)
- `-T type`: Set the notification type (`JobFailed`, `BackupFailed`, `SystemMessage`, `Custom`)
- `-D description`: Add a detailed description to the notification

## Examples

### Basic Notification

Send a simple notification to all admin users:

```bash
sudo immich-distribution.notification -t "System Maintenance Complete"
```

### Notification with Details

Send a detailed notification with level and description:

```bash
sudo immich-distribution.notification \
  -t "Backup Complete" \
  -l "success" \
  -T "SystemMessage" \
  -D "Database backup completed successfully at $(date)"
```

### User-Specific Notification

Send a notification to a specific user:

```bash
sudo immich-distribution.notification \
  -t "Storage Warning" \
  -u "550e8400-e29b-41d4-a716-446655440000" \
  -l "warning" \
  -D "Storage usage is above 90%"
```

### Error Notification

Send an error notification for failed operations:

```bash
sudo immich-distribution.notification \
  -t "Backup Failed" \
  -l "error" \
  -T "BackupFailed" \
  -D "Database backup failed. Please check system logs for details."
```
