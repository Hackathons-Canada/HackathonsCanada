from typing import TYPE_CHECKING

from celery import shared_task
from celery.utils.log import get_task_logger

from django.core.mail import send_mail
from django.apps import apps

if TYPE_CHECKING:
    from core.models import Hacker as HackerType

logger = get_task_logger(__name__)


@shared_task
def send_hackathon_emails(frequency):
    if frequency not in ["weekly", "monthly"]:
        raise ValueError("Frequency must either be 'weekly' or 'monthly'.")

    Hacker: "HackerType" = apps.get_model("core", "Hacker")
    hackers = Hacker.objects.all()

    subject = ""
    message = ""
    emailFrom = "hello@example.com"
    emailTo = []

    if frequency == "weekly":
        emailTo = [
            hacker.email
            for hacker in hackers
            if hacker.email
            and hacker.notification_policy.enabled
            and hacker.notification_policy.weekly
        ]
        subject = "your weekly email"
        message = "Hello! this is your weekly hackathon email!"
    elif frequency == "monthly":
        emailTo = [
            hacker.email
            for hacker in hackers
            if hacker.email
            and hacker.notification_policy.enabled
            and hacker.notification_policy.monthly
        ]
        subject = "your monthly email"
        message = "Hello! this is your monthly hackathon email!"

    send_mail(subject, message, emailFrom, emailTo)
