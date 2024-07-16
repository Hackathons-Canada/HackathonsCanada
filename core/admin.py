# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Category, Hacker, Hackathon
from unfold.admin import ModelAdmin


class HackathonAdmin(ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "location",
    )
    list_filter = ("categories",)
    search_fields = ("name", "location")

    def get_queryset(self, request):
        return self.model.objects.admin()


class UserAdmin(ModelAdmin, BaseUserAdmin):
    pass


class CategoryAdmin(ModelAdmin):
    list_display = (
        "name",
        "color",
    )
    search_fields = ("name",)


admin.site.site_header = "Hackathons Canada Admin"  # set header
admin.site.site_title = "Admin - Hackathons Canada"  # set title
admin.site.index_title = "Welcome to Hackathons Canada Admin Dashboard"

admin.site.register(Hacker, UserAdmin)
admin.site.register(Hackathon, HackathonAdmin)
admin.site.register(Category, CategoryAdmin)
