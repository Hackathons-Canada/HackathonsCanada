import os

from celery import Celery
from celery.schedules import crontab

# from core.models import Hacker

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hackathons_canada.settings")

app = Celery("hackathons_canada")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "send_new_hackathon_email": {
        "task": "core.tasks.send_new_hackathon_email",
        "schedule": crontab(),
        # 'args': Hacker
    }
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
