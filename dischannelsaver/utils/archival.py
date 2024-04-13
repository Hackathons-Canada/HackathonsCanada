import datetime
import re
from typing import Dict

import discord
from django.conf import settings

from dischannelsaver.models import *
import docker


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
    category = await discord.utils.get(guild_id, id=category_id)
    if not category:
        return  # todo log
    date_objs: Dict[datetime, discord.TextChannel] = {}
    channels = await discord.utils.get(guild_id).channels
    for channel in channels:
        dates = get_months(channel.name)
        date_obj = create_datetime(dates[0], dates[1])
        date_objs[date_obj] = channel
    
    for date in sorted(date_objs.keys()):
        await date_objs[date].edit(position=len(date_objs) - 1)


async def call_archiver(channel_id: int):
    COMMAND = 'export -t -c --include-threads all -o " / out / % C" -p 15mb --media --reuse-media --media-dir /media'
    client = docker.from_env()
    container = client.containers.run(
        "tyrrrz/discordchatexporter:stable", COMMAND, detach=True
    )


async def archive_channel(channel_id: int):
    guild = await discord.utils.get(settings.DISCORD_GUILD_ID)
    channel = await discord.utils.get(settings.DISCORD_GUILD_ID, id=channel_id)
    if not channel:
        return  # todo log
    await lock_channel(guild, channel)
    await call_archiver(channel_id)
    # todo verify that the archiver has finished archiving
    await channel.delete()

async def archive_hackathon(hackathon: Hackathon):
    channel = hackathon.channel
    if not channel.discord_id:
        return
    await archive_channel(channel.discord_id)
    channel.is_archived = True
    await channel.save()
    await sort_channels()

