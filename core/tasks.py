from typing import TYPE_CHECKING

from celery import shared_task
from celery.utils.log import get_task_logger

from django.apps import apps
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
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
    
    plaintext_template = get_template("hackathons/new_hackathon_notification.txt")
    html_template = get_template("hackathons/new_hackathon_notification.html")

    context = {
        "hackathons": hackathons,
    }

    text_content = plaintext_template.render(context=context)
    html_content = html_template.render(context=context)

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

    msg = EmailMultiAlternatives(subject, text_content, emailFrom, emailTo)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
