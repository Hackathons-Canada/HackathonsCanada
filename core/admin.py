# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import * # type: ignore


class HackathonAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_date', 'end_date', 'location', 'category', 'is_virtual', 'is_approved')
	list_filter = ('is_virtual', 'is_approved', 'category')
	search_fields = ('name', 'location', 'category')
	readonly_fields = ('created_at', 'updated_at')
	
	def get_queryset(self, request):
		return self.model.objects.admin()

admin.site.site_header = 'Hackathons Canada Admin'  # set header
admin.site.site_title = 'Admin - Hackathons Canada'  # set title
admin.site.index_title = 'Welcome to Hackathons Canada Admin Dashboard'

admin.site.register(Hacker, UserAdmin)
admin.site.register(Hackathon, HackathonAdmin)
admin.site.register(Category)
