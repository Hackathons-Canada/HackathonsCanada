import asyncio
import threading

import discord
from django.apps import AppConfig
from django.conf import settings
import re

intents = discord.Intents.all()
client = discord.Client(intents=intents)

client_thread: threading.Thread
loop: asyncio.AbstractEventLoop


def run(token: str):
    try:
        client.run(token)
    except discord.errors.LoginFailure:
        print("Note: Discord bot token is invalid")
        pass


class DisChannelSaverConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dischannelsaver"
    label = "dischannelsaver"

    def ready(self):
        if settings.DISCORD_TOKEN is None or not re.match(
            r"^([MN][\w-]{23,25})\.([\w-]{6})\.([\w-]{27,39})$", settings.DISCORD_TOKEN
        ):
            print(
                "Note: DISCORD_TOKEN is not set in settings.py or is invalid, if you want to use the discord bot, please set it"
            )
            return
        global client_thread, loop
        client_thread = threading.Thread(target=run, args=[settings.DISCORD_TOKEN])
        client_thread.start()
        loop = asyncio.get_event_loop()
