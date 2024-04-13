from django.db import models

# import discord
from core.models import Hackathon

# Create your models here.


class Settings(models.Model):
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    redirect_uri = models.CharField(max_length=255)


class DiscordUser(models.Model):
    username = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.URLField(
        help_text="URL to the profile picture", blank=True, null=True
    )


class DiscordMessage(models.Model):
    content = models.TextField()
    author = models.ForeignKey(DiscordUser, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(
        "HackathonChannel", on_delete=models.PROTECT, related_name="messages"
    )
    reply_to = models.ForeignKey(
        "DiscordMessage",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="replies",
    )
    hidden = models.BooleanField(
        default=False, help_text="If the message should be shown in web view"
    )
    attachments = models.JSONField(
        default=list, help_text="List of URLs to the attachments"
    )


class HackathonChannel(models.Model):
    hackathon = models.OneToOneField(
        Hackathon, on_delete=models.PROTECT, related_name="channel"
    )
    name = models.CharField(max_length=255)
    discord_id = models.CharField(max_length=18, null=True, blank=True)
    archived = models.BooleanField(
        default=False, help_text="If the channel has been archived or not"
    )
