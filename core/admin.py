# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *

admin.site.site_header = 'Hackathons Canada Admin'  # set header
admin.site.site_title = 'Admin - Hackathons Canada'  # set title
admin.site.index_title = 'Welcome to Hackathons Canada Admin Dashboard'

admin.site.register(Hacker, UserAdmin)
admin.site.register(Hackathon)
admin.site.register(Category)
