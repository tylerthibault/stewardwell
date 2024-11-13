# StewardWell Logging System

A comprehensive logging system for the StewardWell application that provides detailed activity tracking, error monitoring, and security event logging.

## Features

### 1. Multi-level Logging
- Application logs (general activity)
- Error logs (exceptions and errors)
- Security logs (authentication, authorization)
- Performance logs (response times, resource usage)
- Audit logs (user actions and system changes)

### 2. Log Categories
- **INFO**: General application flow and state changes
- **WARNING**: Potential issues that don't affect core functionality
- **ERROR**: Application errors and exceptions
- **SECURITY**: Security-related events
- **AUDIT**: User actions and system modifications

### 3. Automated Maintenance
- Automatic log rotation
- Configurable retention periods
- Compressed archiving
- Scheduled cleanup

### 4. Analysis Tools
- Log searching and filtering
- Activity reports
- Error summaries
- Security event analysis
- Performance metrics

## Directory Structure

```
logs/
├── stewardwell.log     # Main application log
├── error.log          # Error and exception log
├── security.log       # Security events log
├── performance.log    # Performance metrics
├── audit.log         # User action audit log
├── archived/         # Compressed old logs
└── analysis/         # Log analysis reports
```

## Configuration

Configuration options are available in `config.py`:

```python
# Log file paths and names
LOG_DIR = 'logs'
LOG_FILENAME = 'stewardwell.log'
ERROR_LOG_FILENAME = 'error.log'

# Log rotation settings
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Log levels
LOG_LEVEL = 'INFO'
ERROR_LOG_LEVEL = 'ERROR'
```

## Usage

### Command Line Interface

The `manage_logs.py` script provides various commands for log management:

```bash
# Show recent errors
python manage_logs.py show-errors --hours 24

# Generate analysis report
python manage_logs.py analyze --days 7

# Archive old logs
python manage_logs.py archive-logs --days 30

# Generate daily report
python manage_logs.py generate-report

# Search logs
python manage_logs.py search "error message"

# Show system status
python manage_logs.py status
```

### Automated Maintenance

Set up automated maintenance tasks using `setup_log_maintenance.py`:

```bash
python setup_log_maintenance.py
```

This will configure:
- Daily log archiving (midnight)
- Daily report generation (1 AM)
- Weekly cleanup (2 AM on Sundays)

### Logging in Code

#### Basic Logging
```python
from app.utils.logger import ActivityLogger

logger = ActivityLogger('module_name')

# Log general activity
logger.log_activity(user_id, 'action_name', details={})

# Log errors
logger.log_error(user_id, 'error_type', error_details)
```

#### Decorator Usage
```python
from app.utils.logger import log_action

@log_action('action_name')
def your_function():
    # Function code here
    pass
```

## Log Formats

### Application Log
```
[timestamp] - level - module - user_id - message
```

### Error Log
```
[timestamp] - ERROR - module - user_id - error_type - message - traceback
```

### Security Log
```
[timestamp] - SECURITY - level - user_id - action - details
```

### Audit Log
```
[timestamp] - AUDIT - user_id - action - resource - changes
```

## Analysis Reports

Daily reports include:
- Error counts and types
- Active user statistics
- Security event summary
- Performance metrics
- Resource usage

Reports are saved in JSON format in `logs/analysis/`.

## Security Considerations

1. Log files are automatically rotated to prevent disk space issues
2. Sensitive information is automatically redacted
3. Access to log files is restricted by file permissions
4. Archived logs are compressed and encrypted

## Best Practices

1. Use appropriate log levels
2. Include relevant context in log messages
3. Don't log sensitive information
4. Use structured logging when possible
5. Regular monitoring of error logs
6. Review security logs daily
7. Archive logs according to retention policy

## Troubleshooting

### Common Issues

1. Log files not rotating
```bash
# Check permissions
chmod 644 logs/*.log
chmod 755 logs/archived
```

2. Missing logs
```bash
# Verify log configuration
python manage_logs.py status
```

3. Performance issues
```bash
# Check log sizes
du -sh logs/*
```

### Monitoring

Set up alerts for:
- High error rates
- Security incidents
- Disk space usage
- Failed log rotations

## Integration

### Email Notifications
Configure in `config.py`:
```python
MAIL_SERVER = 'smtp.example.com'
MAIL_PORT = 587
MAIL_USERNAME = 'alerts@example.com'
MAIL_PASSWORD = 'password'
```

### External Services
Support for forwarding logs to:
- Syslog
- ELK Stack
- Cloud logging services

## Contributing

When adding new features:
1. Follow existing log formats
2. Update documentation
3. Add appropriate log messages
4. Include tests for new functionality

## License

This logging system is part of the StewardWell application and is covered under the same license terms.
