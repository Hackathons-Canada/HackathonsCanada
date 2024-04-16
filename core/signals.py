from typing import TYPE_CHECKING

from celery.utils.log import get_task_logger
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Hackathon

if TYPE_CHECKING:
    from core.models import Hacker

logger = get_task_logger(__name__)


@receiver(post_save, sender=Hackathon)
async def new_hackathon_notif(sender, instance, created, **kwargs):
    if not created:
        return  # only notify on creation
    logger.debug(f"New hackathon created: {instance}")
    await Hacker.objects.filter(
        saved_categories__in=instance.categories.all()  # redo this once u setup the GIS db
    ).anotify()
