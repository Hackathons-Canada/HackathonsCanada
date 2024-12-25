import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

app = Celery("hackathons_canada")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send_weekly_emails": {
        "task": "core.tasks.send_hackathon_emails",
        "schedule": crontab(day_of_week="1"),
        "args": ["weekly"],
    },
    "send_monthly_emails": {
        "task": "core.tasks.send_hackathon_emails",
        "schedule": crontab(day_of_month="1"),
        "args": ["monthly"],
    },
}
