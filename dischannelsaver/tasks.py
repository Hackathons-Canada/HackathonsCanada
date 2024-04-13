from celery.utils.log import get_task_logger
from django.conf import settings
from django.utils import timezone

from canadahackers.celery import app
from dischannelsaver.models import *
from dischannelsaver.utils.archival import archive_hackathon

logger = get_task_logger(__name__)

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
