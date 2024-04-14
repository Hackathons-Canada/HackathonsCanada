import datetime
import re
import time
from typing import Dict

import discord
from discord import CategoryChannel
from django.conf import settings
from django.utils import timezone

from dischannelsaver.models import *
import docker

from ..apps import client


def generate_discord_timestamp(date: datetime.datetime):
    return f"<t:{int(date.timestamp())}:R"


async def create_channel(hackathon: Hackathon):
    channel_name = generate_channel_name(hackathon)

    category = await discord.utils.get(
        client.guilds[0].categories, id=settings.DISCORD_ACTIVE_CATEGORY_ID
    )

    channel = await category.create_text_channel(
        channel_name, reason="Creating hackathon channel"
    )

    embed = discord.Embed(title=hackathon.name, color=discord.Color.green())
    embed.add_field(name="Website", value=hackathon.website)
    embed.add_field(
        name="Categories",
        value=", ".join([category.name for category in hackathon.categories.all()]),
    )
    embed.add_field(
        name="Event dates",
        value=f"{generate_discord_timestamp(hackathon.start_date)} - {generate_discord_timestamp(hackathon.end_date)}",
    )
    embed.add_field(
        name="Application dates",
        value=f"{generate_discord_timestamp(hackathon.application_start)} - {generate_discord_timestamp(hackathon.application_deadline)}",
    )
    channel.send(embed=embed)
    HackathonChannel.objects.create(
        hackathon=hackathon, name=channel_name, discord_id=channel.id, archived=False
    )


def generate_channel_name(hackathon: Hackathon):
    """

    :param hackathon:
    :return: discord channel name (e.g. hackathon-name-Jan-3-5), or if it's a 1-day hackathon, hackathon-name-Jan-24
    """
    name = hackathon.name.casefold().replace(" ", "-")
    if hackathon.end_date.day == hackathon.start_date.day:
        return f"{name}-{hackathon.start_date.strftime('%b-%-d')}"
    return f"{name}-{hackathon.start_date.strftime('%b-%-d')}-{hackathon.end_date.strftime('%-d')}"


def create_datetime(month, day) -> datetime.datetime:
    """
    Creates a datetime object for the given month and day,
    assuming the year is the one where the month is closest to now.

    Args:
            month (int): Month (1-12).
            day (int): Day (1-31).

    Returns:
            datetime.datetime: The datetime object.

    Raises:
            ValueError: If the month or day is out of range.
    """

    def month_name_to_number(name):
        return {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }[name.lower()]

    now = datetime.datetime.now()
    month = month_name_to_number(month)

    # Check for valid month and day
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12")
    if day < 1 or day > 31:
        raise ValueError("Day must be between 1 and 31")

    # Try current year first
    potential_date = datetime.datetime(year=now.year, month=month, day=day)

    # Check if the month has already passed in the current year
    if potential_date < now:
        # Try next year if month has passed
        next_year = now.year + 1
    else:
        # Keep current year if month is in the future
        next_year = now.year

    # Create datetime object for next year
    next_year_date = datetime.datetime(next_year, month, day)

    # Choose the date closest to now
    return min(potential_date, next_year_date)


def get_months(channel_name):
    """

    :param channel_name:
    :return: month (e.g. Jan), day (e.g. 0
    """
    PATTERN = r"^.*-(\w{3})-(\d+)(?:-(\d+))?$"
    match = re.match(PATTERN, channel_name)
    if not match:
        return None
    if match.groups()[
        2
    ]:  # If the third group is not None (i.e. the end date is present)
        return match.groups()
    return match.groups() + (match.groups()[1],)


async def lock_channel(guild: discord.Guild, channel: discord.TextChannel):
    everyone = discord.utils.get(guild.roles, name="@everyone")
    await channel.set_permissions(
        everyone, send_messages=False, reason="Archiving channel"
    )


async def sort_channels():
    guild_id = settings.DISCORD_GUILD_ID
    category_id = settings.DISCORD_ARCHIVE_CATEGORY
    category: CategoryChannel = await discord.utils.get(guild_id, id=category_id)
    if not category:
        return  # todo log
    date_objs: Dict[datetime, discord.TextChannel] = {}
    channels = category.text_channels
    for channel in channels:
        dates = get_months(channel.name)
        date_obj = create_datetime(dates[0], dates[1])
        date_objs[date_obj] = channel

    for date in sorted(date_objs.keys()):
        await date_objs[date].edit(position=len(date_objs) - 1)


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
    time = await call_archiver(channel_id)
    # todo verify that the archiver has finished archiving
    await channel.delete()
    return time


async def archive_hackathon(hackathon: Hackathon):
    channel = hackathon.channel
    if not channel.discord_id:
        return
    time_taken = await archive_channel(channel.discord_id)
    channel.is_archived = True
    channel.archived_at = timezone.now()
    channel.archived_time = datetime.timedelta(seconds=time_taken)
    await channel.save()
    await sort_channels()
