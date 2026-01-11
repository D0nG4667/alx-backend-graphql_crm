"""
CRM App Configuration Settings
"""

# Django INSTALLED_APPS entry
INSTALLED_APPS = [
    "django_crontab",
]

# CRM App Settings
CRM_SETTINGS = {
    # Heartbeat logging settings
    "HEARTBEAT_LOG_FILE": "/tmp/crm_heartbeat_log.txt",
    "HEARTBEAT_INTERVAL": "*/5 * * * *",  # Every 5 minutes
    # Low stock alert settings
    "LOW_STOCK_THRESHOLD": 10,
    "RESTOCK_AMOUNT": 10,
    "LOW_STOCK_LOG_FILE": "/tmp/low_stock_updates_log.txt",
    "LOW_STOCK_UPDATE_INTERVAL": "0 */12 * * *",  # Every 12 hours
    # Customer cleanup settings
    "INACTIVE_CUSTOMER_DAYS": 365,
    "CUSTOMER_CLEANUP_LOG_FILE": "/tmp/customer_cleanup_log.txt",
    "CUSTOMER_CLEANUP_INTERVAL": "0 2 * * 0",  # Every Sunday at 2:00 AM
    # Order reminders settings
    "ORDER_REMINDER_DAYS": 7,
    "ORDER_REMINDERS_LOG_FILE": "/tmp/order_reminders_log.txt",
    "ORDER_REMINDERS_INTERVAL": "0 8 * * *",  # Every day at 8:00 AM
    # GraphQL settings
    "GRAPHQL_ENDPOINT": "http://localhost:8000/graphql",
}

# Cron job intervals
CRON_INTERVALS = {
    "HEARTBEAT": "*/5 * * * *",
    "LOW_STOCK_UPDATE": "0 */12 * * *",
    "CUSTOMER_CLEANUP": "0 2 * * 0",
    "ORDER_REMINDERS": "0 8 * * *",
}

# Django Crontab Jobs Configuration
CRONJOBS = [
    ("*/5 * * * *", "crm.cron.log_crm_heartbeat"),
    ("0 */12 * * *", "crm.cron.update_low_stock"),
]
