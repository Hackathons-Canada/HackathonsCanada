from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from canadahackers.celery import app
from dischannelsaver.models import *
from dischannelsaver.utils.archival import archive_hackathon, create_channel

logger = get_task_logger(__name__)


@receiver(post_save, sender=Hackathon)
async def my_handler(sender, instance, created, **kwargs):
    if created or not instance.channel.exists():
        logger.info(f"Creating channel for {instance}")
        await create_channel(instance)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour=0, minute=0), archive_channels) # every day at midnight


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
