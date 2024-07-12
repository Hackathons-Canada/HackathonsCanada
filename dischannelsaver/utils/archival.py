import datetime
import time

import discord
import docker  # type: ignore
from django.conf import settings
from django.utils import timezone

from core.models import Hackathon

from .disc import lock_channel, sort_channels


async def call_archiver(channel_id: int) -> float:
    """
    Calls the discord chat exporter to archive a channel
    :param channel_id:
    :return: time taken to archive the channel in seconds
    """
    COMMAND = f'export -t {settings.DISCORD_TOKEN} -c {channel_id} --include-threads all -o " / out / % C" -p 15mb --media --reuse-media --media-dir /media '
    VOLUMES = ["/media:/media", "/out:/out"]  # see docker-compose.yml section celery
    client = docker.from_env()
    start = time.perf_counter()
    container = client.containers.run(
        "tyrrrz/discordchatexporter:stable", COMMAND, detach=True, volumes=VOLUMES
    )
    container.wait()
    end = time.perf_counter()
    return end - start


async def archive_channel(channel_id: int):
    guild = await discord.utils.get(settings.DISCORD_GUILD_ID)
    channel = await discord.utils.get(settings.DISCORD_GUILD_ID, id=channel_id)
    if not channel:
        return  # todo log
    await lock_channel(guild, channel)
    exec_time = await call_archiver(channel_id)
    # todo verify that the archiver has finished archiving
    await channel.delete()
    return exec_time


async def archive_hackathon(hackathon: Hackathon):
    channel = hackathon.channel
    if not channel.discord_id:
        return
    time_taken = await archive_channel(channel.discord_id)
    channel.archived = True
    channel.archived_at = timezone.now()
    channel.archived_time = datetime.timedelta(seconds=time_taken)
    await channel.save()
    await sort_channels()
