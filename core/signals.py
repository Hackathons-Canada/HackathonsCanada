from typing import TYPE_CHECKING

from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.tasks import send_instant_notification

from core.models import Hackathon

if TYPE_CHECKING:
    pass

logger = get_task_logger(__name__)


@receiver(
    post_save, sender=Hackathon
)  # todo: change to custom "Hackathon posted" signal
async def new_hackathon_notif(sender, instance, created, **kwargs):
    if not created:
        return  # only notify on creation
    send_instant_notification.delay(instance.id)
    logger.debug(f"New hackathon created: {instance}")
