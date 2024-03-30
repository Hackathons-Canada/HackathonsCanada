from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(Hacker, UserAdmin)
admin.site.register(Hackathon)
