import re

import discord
from django.conf import settings

from dischannelsaver.models import *


def generate_channel_name(hackathon: Hackathon):
	"""
	
	:param hackathon:
	:return: discord channel name (e.g. hackathon-name-Jan-3-5), or if it's a 1-day hackathon, hackathon-name-Jan-24
	"""
	if hackathon.end_date.day == hackathon.start_date.day:
		return f"{hackathon.name.casefold().replace(" ", "-")}-{hackathon.start_date.strftime('%b-%-d')}"
	return f"{hackathon.name.casefold().replace(" ", "-")}-{hackathon.start_date.strftime('%b-%-d')}-{hackathon.end_date.strftime('%-d')}"


def get_months(channel_name):
	"""
	
	:param channel_name:
	:return: month (e.g. Jan), day (e.g. 0
	"""
	PATTERN = r'^.*-(\w{3})-(\d+)(?:-(\d+))?$'
	match = re.match(PATTERN, channel_name)
	if not match:
		return None
	if match.groups()[2]:  # If the third group is not None (i.e. the end date is present)
		return match.groups()
	return match.groups() + (None,)


async def lock_channel(guild: discord.Guild, channel: discord.TextChannel):
	everyone = discord.utils.get(guild.roles, name="@everyone")
	await channel.set_permissions(everyone, send_messages=False, reason="Archiving channel")


async def sort_channels():
	guild_id = settings.DISCORD_GUILD_ID
	channel_id = settings.DISCORD_ARCHIVE_CATEGORY


async def archive_message(message: discord.Message, channel: HackathonChannel):
	author = await DiscordUser.objects.aget_or_create(discord_id=message.author.id,
	                                                  defaults={"username": message.author.name,
	                                                            "nickname": message.author.nick,
	                                                            "profile_picture": message.author.avatar.url})
	# if message.attachments:
	# 	for attachment in message.attachments:
	# 		await attachment.save(f"attachments/{message.id}-{attachment.id}")  # todo this is not a good way to save attachments: just a temp solution
	await DiscordMessage.objects.acreate(author=author, content=message.content,
	                                     attachements=[str(uri) for uri in message.attachments],
	                                     created_at=message.created_at, channel=channel, reply_to=message.reference)
	await message.delete()


async def archive_channel(channel_id: int):
	guild = await discord.utils.get(settings.DISCORD_GUILD_ID)
	channel = await discord.utils.get(settings.DISCORD_GUILD_ID, id=channel_id)
	if not channel:
		return  # todo log
	await lock_channel(guild, channel)
	channel_obj = await HackathonChannel.objects.aget(discord_id=channel_id)
	async for message in await channel.history(limit=None).flatten():
		await archive_message(message, channel_obj)


# await channel.edit(category=discord.utils.get(channel.guild.categories, id=settings.DISCORD_ARCHIVE_CATEGORY))

async def archive_hackathon(hackathon: Hackathon):
	channel = hackathon.channel
	if not channel.discord_id:
		return
	await archive_channel(channel.discord_id)
