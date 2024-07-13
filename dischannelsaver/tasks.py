from typing import TYPE_CHECKING

from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from hackathons_canada.celery import app
from dischannelsaver.utils.archival import archive_hackathon
from dischannelsaver.utils.disc import create_channel, sort_channels

if TYPE_CHECKING:
    from core.models import Hackathon, Hacker

logger = get_task_logger(__name__)
hacker: "Hacker" = get_user_model()  # type: ignore


@receiver(post_save, sender=Hackathon)
async def channel_create(sender, instance, created, **kwargs):
    if created or not instance.channel.exists():
        logger.info(f"Creating channel for {instance}")
        await create_channel(instance)
    await sort_channels()  # sort channels after creating a new one


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0), archive_channels
    )  # every day at midnight


@app.task
async def archive_channels():
    if not settings.DISCORD_ARCHIVE_ENABLED:
        logger.info("Channel archiving is disabled... skipping")
        return
    logger.info("Archiving channels")
    achievable_channels = Hackathon.objects.prefetch_related("channel").exclude(
        channel__is_archived=False,
        start_date__lte=timezone.now(),
        start_date__gte=timezone.now()
        - timezone.timedelta(days=settings.DISCORD_ARCHIVE_AFTER),
    )

    if not await achievable_channels.aexists():
        logger.info("No channels to archive.. skipping")
        return
    logger.info(f"Archiving {await archive_channels.acount()} channels")
    async for hackathon in achievable_channels:
        await archive_hackathon(hackathon)
