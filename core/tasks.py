from typing import TYPE_CHECKING

from celery import shared_task
from celery.utils.log import get_task_logger

from django.core.mail import send_mail
from django.apps import apps
from django.utils import timezone

if TYPE_CHECKING:
    from core.models import Hacker as HackerType, Hackathon as HackathonType

logger = get_task_logger(__name__)


@shared_task
def send_hackathon_emails(frequency):
    if frequency not in ["weekly", "monthly"]:
        raise ValueError("Frequency must either be 'weekly' or 'monthly'.")

    Hacker: "HackerType" = apps.get_model("core", "Hacker")
    hackers = Hacker.objects.all()

    tdy_date = timezone.now()
    Hackathon: "HackathonType" = apps.get_model("core", "Hackathon")
    hackathons = Hackathon.objects.filter(start_date__gt=tdy_date)

    subject = ""
    emailFrom = "hello@example.com"
    emailTo = []
    message = "New hackathons found:\n"
    message += "<ul>\n"
    for hackathon in hackathons:
        message += "  <li>"
        message += hackathon.name
        message += "</li>\n"
    message += "</ul>\n"

    if frequency == "weekly":
        emailTo = [
            hacker.email
            for hacker in hackers
            if hacker.email
            and hacker.notification_policy.enabled
            and hacker.notification_policy.weekly
        ]
        subject = "your weekly email"
    elif frequency == "monthly":
        emailTo = [
            hacker.email
            for hacker in hackers
            if hacker.email
            and hacker.notification_policy.enabled
            and hacker.notification_policy.monthly
        ]
        subject = "your monthly email"

    send_mail(subject, message, emailFrom, emailTo)
