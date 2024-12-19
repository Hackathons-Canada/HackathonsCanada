from celery import shared_task
from django.core.mail import send_mass_mail, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

BATCH_SIZE = settings.EMAIL_BATCH_SIZE or 50  # default to 50


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_hackathon_digest(self):
    """Send digest emails to users based on their preferences"""
    logger.info("Starting hackathon digest email task")
    from .models import EmailPreferences

    try:
        # Get all users due for an email
        preferences = EmailPreferences.objects.select_related("user").filter(
            user__is_active=True, frequency__in=["weekly", "monthly"]
        )

        email_batch: List[Tuple[str, str, str, List[str]]] = []
        processed_count = 0
        error_count = 0

        for pref in preferences:
            try:
                if not pref.is_due_for_email():
                    continue

                hackathons = pref.get_relevant_hackathons()

                if not hackathons:
                    continue

                context = {
                    "user": pref.user,
                    "hackathons": hackathons,
                    "frequency": pref.frequency,
                    "unsubscribe_url": f"{settings.SITE_URL}/preferences/email/",  # todo: Impl
                }

                html_content = render_to_string("email/hackathon_digest.html", context)
                plain_content = strip_tags(html_content)

                subject = f"Your {pref.frequency} Hackathon Digest"

                email_batch.append(
                    (
                        subject,
                        plain_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [pref.user.email],
                    )
                )

                processed_count += 1

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Error processing digest for user {pref.user.email}: {str(e)}",
                    exc_info=True,
                )

        connection = get_connection(fail_silently=False)

        for i in range(0, len(email_batch), BATCH_SIZE):
            batch_slice = email_batch[i : i + BATCH_SIZE]
            try:
                send_mass_mail(batch_slice, fail_silently=False, connection=connection)

                # Update last_email_sent for successful batch
                for subject, _, _, recipients in batch_slice:
                    EmailPreferences.objects.filter(user__email__in=recipients).update(
                        last_email_sent=timezone.now()
                    )

            except Exception as e:
                logger.error(
                    f"Error sending email batch {i//BATCH_SIZE + 1}: {str(e)}",
                    exc_info=True,
                )
                raise self.retry(exc=e)

        logger.info(
            f"Digest task completed. Processed: {processed_count}, "
            f"Errors: {error_count}, Total emails: {len(email_batch)}"
        )

    except Exception as e:
        logger.error(f"Critical error in digest task: {str(e)}", exc_info=True)
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_instant_notification(self, hackathon_id):
    """Send instant notifications for new hackathons"""
    logger.info(f"Starting instant notification task for hackathon {hackathon_id}")

    try:
        from .models import Hackathon, EmailPreferences

        try:
            hackathon = Hackathon.objects.get(id=hackathon_id)
        except Hackathon.DoesNotExist:
            logger.error(f"Hackathon {hackathon_id} not found")
            return

        preferences = EmailPreferences.objects.select_related("user").filter(
            frequency="instant", user__is_active=True
        )  # todo: add other preferences such as distance into account

        email_batch = []
        processed_count = 0
        error_count = 0

        for pref in preferences:
            try:
                # Check if hackathon matches user preferences
                relevant_hackathons = pref.get_relevant_hackathons()
                if hackathon not in relevant_hackathons:
                    continue

                context = {
                    "user": pref.user,
                    "hackathon": hackathon,
                    "unsubscribe_url": f"{settings.SITE_URL}/preferences/email/",
                }

                html_content = render_to_string(
                    "email/instant_notification.html", context
                )
                plain_content = strip_tags(html_content)

                subject = f"New Hackathon Alert: {hackathon.name}"

                email_batch.append(
                    (
                        subject,
                        plain_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [pref.user.email],
                    )
                )

                processed_count += 1

            except Exception as e:
                error_count += 1
                logger.error(
                    f"Error processing instant notification for user {pref.user.email}: {str(e)}",
                    exc_info=True,
                )

        connection = get_connection(fail_silently=False)

        for i in range(0, len(email_batch), BATCH_SIZE):
            batch_slice = email_batch[i : i + BATCH_SIZE]
            try:
                send_mass_mail(batch_slice, fail_silently=False, connection=connection)

            except Exception as e:
                logger.error(
                    f"Error sending instant notification batch {i//BATCH_SIZE + 1}: {str(e)}",
                    exc_info=True,
                )
                raise self.retry(exc=e)

        logger.info(
            f"Instant notification task completed. Processed: {processed_count}, "
            f"Errors: {error_count}, Total emails: {len(email_batch)}"
        )

    except Exception as e:
        logger.error(
            f"Critical error in instant notification task: {str(e)}", exc_info=True
        )
        raise self.retry(exc=e)
