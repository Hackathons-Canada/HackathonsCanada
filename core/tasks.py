from celery import shared_task
from celery.utils.log import get_task_logger

from django.conf import settings
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = get_task_logger(__name__)


@shared_task
def send_hackathon_digest():
    """Send digest emails to users based on their preferences"""
    from .models import EmailPreferences

    # Get all users due for an email
    preferences = EmailPreferences.objects.select_related("user").filter(
        user__is_active=True, frequency__in=["daily", "weekly", "monthly"]
    )

    email_batch = []

    for pref in preferences:
        if not pref.is_due_for_email():
            continue

        hackathons = pref.get_relevant_hackathons()

        if not hackathons:
            continue

        context = {
            "user": pref.user,
            "hackathons": hackathons,
            "frequency": pref.frequency,
            "unsubscribe_url": f"{settings.SITE_URL}/preferences/email/",
        }

        html_content = render_to_string("email/hackathon_digest.html", context)
        plain_content = strip_tags(html_content)

        subject = f"Your {pref.frequency} Hackathon Digest"

        email_batch.append(
            (subject, plain_content, settings.DEFAULT_FROM_EMAIL, [pref.user.email])
        )

        # Update last_email_sent timestamp
        pref.last_email_sent = timezone.now()
        pref.save()

    # Send emails in batch
    if email_batch:
        send_mass_mail(email_batch, fail_silently=False)


@shared_task
def send_instant_notification(hackathon_id):
    """Send instant notifications for new hackathons"""
    from .models import Hackathon, EmailPreferences

    try:
        hackathon = Hackathon.objects.get(id=hackathon_id)
    except Hackathon.DoesNotExist:
        return

    preferences = EmailPreferences.objects.select_related("user").filter(
        frequency="instant", user__is_active=True
    )

    email_batch = []

    for pref in preferences:
        # Check if hackathon matches user preferences
        relevant_hackathons = pref.get_relevant_hackathons()
        if hackathon not in relevant_hackathons:
            continue

        context = {
            "user": pref.user,
            "hackathon": hackathon,
            "unsubscribe_url": f"{settings.SITE_URL}/preferences/email/",
        }

        html_content = render_to_string("email/instant_notification.html", context)
        plain_content = strip_tags(html_content)

        subject = f"New Hackathon Alert: {hackathon.name}"

        email_batch.append(
            (subject, plain_content, settings.DEFAULT_FROM_EMAIL, [pref.user.email])
        )

    if email_batch:
        send_mass_mail(email_batch, fail_silently=False)
