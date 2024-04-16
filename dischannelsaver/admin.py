from functools import wraps

from django.contrib import admin

from dischannelsaver.models import HackathonChannel, Settings
from dischannelsaver.utils.archival import archive_hackathon
from asgiref.sync import async_to_sync


# Register your models here.
def archive_channels(modeladmin, request, queryset):
    async def inner():
        async for channel in queryset:
            await archive_hackathon(channel.hackathon)

    return async_to_sync(inner)


class HackathonChannelAdmin(admin.ModelAdmin):
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


admin.site.register(Settings)
admin.site.register(HackathonChannel, HackathonChannelAdmin)
