# CRM Application Setup Guide

This guide provides step-by-step instructions to set up and run the CRM application with Celery and Celery Beat for scheduled tasks.

## Prerequisites

- Python 3.12+
- Django 6.0+
- Redis (for Celery broker)

## Installation and Setup

### 1. Install Redis

**On Windows:**
Download and install Redis from: https://github.com/microsoftarchive/redis/releases

Or use Windows Subsystem for Linux (WSL):
```bash
wsl
sudo apt-get install redis-server
```

**On macOS:**
```bash
brew install redis
```

**On Linux:**
```bash
sudo apt-get install redis-server
```

### 2. Install Dependencies

All required packages are already specified in `pyproject.toml`. Install them using:

```bash
pip install -e .
```

This installs:
- `celery>=5.6.2`
- `django-celery-beat>=2.1.0`
- `django-crontab>=0.7.1`
- `gql[all]>=4.0.0`
- `graphene-django>=3.2.3`
- And other dependencies

### 3. Run Django Migrations

Apply migrations to set up the database for Celery Beat:

```bash
python manage.py migrate
```

This creates the necessary tables for storing scheduled tasks.

### 4. Start Redis Server

**On Windows (if installed as service):**
Redis should start automatically.

**On macOS/Linux:**
```bash
redis-server
```

Or start it in the background:
```bash
redis-server --daemonize yes
```

### 5. Start Celery Worker

In a new terminal, from the project root directory:

```bash
celery -A crm worker -l info
```

This starts the Celery worker that processes scheduled tasks.

### 6. Start Celery Beat (Scheduler)

In another new terminal, from the project root directory:

```bash
celery -A crm beat -l info
```

This starts the Celery Beat scheduler that triggers tasks at scheduled times.

## Scheduled Tasks

### Generate CRM Report

- **Schedule**: Every Monday at 6:00 AM (UTC)
- **Task**: `crm.tasks.generate_crm_report`
- **What it does**:
  - Queries the GraphQL endpoint for total customers, orders, and revenue
  - Logs the report to `/tmp/crm_report_log.txt`
  - Report format: `YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue`

## Verifying the Setup

### Check Celery Worker is Running
The worker should display output like:
```
[2025-01-11 10:30:00,000: INFO/MainProcess] celery@hostname ready.
```

### Check Celery Beat is Running
Celery Beat should display scheduled tasks:
```
[2025-01-11 10:31:00,000: INFO/MainProcess] Scheduler: Sending due task generate-crm-report (crm.tasks.generate_crm_report)
```

### View Generated Reports
Check the report log file:
```bash
cat /tmp/crm_report_log.txt
```

Expected output:
```
2025-01-13 06:00:00 - Report: 15 customers, 45 orders, 5000.50 revenue
```

## Troubleshooting

### Redis Connection Error
```
Error: Cannot connect to redis://localhost:6379/0
```
**Solution**: Ensure Redis server is running. Check with: `redis-cli ping` (should return `PONG`)

### Task Not Executing
1. Verify Celery Worker is running
2. Verify Celery Beat is running
3. Check worker logs for errors
4. Ensure `crm/__init__.py` imports the Celery app

### Permission Denied on Log File
```
Permission denied: '/tmp/crm_report_log.txt'
```
**Solution**: Ensure write permissions on `/tmp` directory or change log path in `crm/settings.py`

## Configuration Files

- **crm/celery.py**: Initializes Celery app and auto-discovers tasks
- **crm/__init__.py**: Imports and loads the Celery app on startup
- **crm/tasks.py**: Contains the `generate_crm_report` task
- **crm/settings.py**: Celery configuration and beat schedule
- **crm/cron.py**: Django crontab jobs (legacy, runs independently)

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django-Celery-Beat](https://github.com/celery/django-celery-beat)
- [Redis Documentation](https://redis.io/documentation)
