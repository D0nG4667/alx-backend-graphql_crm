import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")

app = Celery("crm")

# Load configuration from Django settings, all celery configuration should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
