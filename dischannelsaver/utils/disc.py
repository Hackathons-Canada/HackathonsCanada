import datetime
from typing import Dict

import discord
from discord import CategoryChannel
from django.conf import settings

from core.models import Hackathon
from dischannelsaver.apps import client
from dischannelsaver.models import HackathonChannel
from dischannelsaver.utils.nomenclature import (
    create_datetime,
    generate_channel_name,
    generate_discord_timestamp,
    get_months,
)
__all__ = ["create_channel", "lock_channel", "sort_channels"]


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
