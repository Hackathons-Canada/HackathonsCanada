from asgiref.sync import async_to_sync
from django.contrib import admin

from dischannelsaver.models import HackathonChannel, Settings
from dischannelsaver.utils.archival import archive_hackathon
from unfold.admin import ModelAdmin


# Register your models here.
def archive_channels(modeladmin, request, queryset):
    async def inner():
        async for channel in queryset:
            await archive_hackathon(channel.hackathon)

    return async_to_sync(inner)


class HackathonChannelAdmin(ModelAdmin):
    list_display = (
        "name",
        "hackathon",
        "discord_id",
        "archived",
        "archived_at",
        "archived_time",
    )
    list_filter = ("archived",)
    search_fields = ("name", "hackathon__name", "discord_id")
    readonly_fields = ("archived_at", "archived_time")

    actions = [archive_channels]


class SettingsAdmin(ModelAdmin):
    pass


admin.site.register(Settings, SettingsAdmin)
admin.site.register(HackathonChannel, HackathonChannelAdmin)
