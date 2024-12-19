from typing import TYPE_CHECKING

from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Hackathon

if TYPE_CHECKING:
    pass

logger = get_task_logger(__name__)


@receiver(post_save, sender=Hackathon)
async def new_hackathon_notif(sender, instance, created, **kwargs):
    if not created:
        return  # only notify on creation
    # todo run a task to notify hackers who signed up for this hackathon and are their preferences are set to receive notifications within the radius of the hackathon
    logger.debug(f"New hackathon created: {instance}")
