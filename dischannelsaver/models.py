from django.db import models

# import discord
from core.models import Hackathon

# Create your models here.


class Settings(models.Model):
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    redirect_uri = models.CharField(max_length=255)


class HackathonChannel(models.Model):
    hackathon = models.OneToOneField(
        Hackathon, on_delete=models.PROTECT, related_name="channel"
    )
    name = models.CharField(max_length=255)
    discord_id = models.CharField(max_length=18, null=True, blank=True)
    archived = models.BooleanField(
        default=False, help_text="If the channel has been archived or not"
    )
    archived_at = models.DateTimeField(
        null=True, blank=True, help_text="When the channel was archived"
    )
    archived_time = models.DurationField(
        null=True, blank=True, help_text="How long the channel was archived for"
    )
    
