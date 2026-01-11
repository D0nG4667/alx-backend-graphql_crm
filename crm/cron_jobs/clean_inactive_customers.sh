#!/bin/bash

# Customer Cleanup Script
# Deletes customers with no orders in the past year

# Get the absolute path to the Django project
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Timestamp for logging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Python command to delete inactive customers
PYTHON_COMMAND="
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find and delete customers with no orders since a year ago
deleted_customers = Customer.objects.filter(
    created_at__lt=one_year_ago,
    orders__isnull=True
).distinct()

count = deleted_customers.count()
deleted_customers.delete()

print(f'{count}')
"

# Execute the Python command using Django shell
DELETED_COUNT=$(cd "$PROJECT_DIR" && python manage.py shell <<EOF
$PYTHON_COMMAND
EOF
)

# Log the result
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
