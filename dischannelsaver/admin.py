from django.contrib import admin

from dischannelsaver.models import HackathonChannel, Settings

# Register your models here.


admin.site.register(Settings)
admin.site.register(HackathonChannel)
