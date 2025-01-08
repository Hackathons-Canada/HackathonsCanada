# Register your models here.
from allauth.account import app_settings
from allauth.account.admin import (
    EmailAddressAdmin as BaseEmailAddress,
)
from allauth.account.admin import (
    EmailConfirmationAdmin as BaseEmailConfirmation,
)
from allauth.account.models import EmailAddress, EmailConfirmation
from django.contrib import admin
from django.contrib.auth.admin import (
    GroupAdmin as BaseGroupAdmin,
    UserAdmin as BaseUserAdmin,
)
from django.contrib.auth.models import Group
from django.contrib.redirects.models import Redirect
from django.db import models
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm
from django.contrib.redirects.admin import RedirectAdmin as BaseRedirectAdmin
from .models import Category, Hackathon, Hacker, School
from .models import HackathonLocation


class RedirectAdmin(ModelAdmin, BaseRedirectAdmin):
    pass


class EmailAddressAdmin(BaseEmailAddress, ModelAdmin):
    pass


class EmailConfirmationAdmin(ModelAdmin, BaseEmailConfirmation):
    pass


class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    list_display = (
        "name",
        "display_permissions",
        "member_count",
    )
    search_fields = ("name",)

    @display(description=_("Permissions"))
    def display_permissions(self, instance):
        return instance.permissions.count()

    @display(description=_("Members"))
    def member_count(self, instance):
        return instance.user_set.count()


class HackathonAdmin(ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "end_date",
        "location",
    )
    list_filter = ("categories",)
    search_fields = ("name", "location__name")


class HackerAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    # add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = [
        "display_header",
        "is_active",
        "display_staff",
        "display_superuser",
        "display_created",
        "display_hackathons",
    ]

    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }
    readonly_fields = ["last_login", "date_joined"]

    @display(description=_("User"))
    def display_header(self, instance: Hacker):
        return instance.username

    @display(description=_("Staff"), boolean=True)
    def display_staff(self, instance: Hacker):
        return instance.is_staff

    @display(description=_("Superuser"), boolean=True)
    def display_superuser(self, instance: Hacker):
        return instance.is_superuser

    @display(description=_("Created"))
    def display_created(self, instance: Hacker):
        return instance.date_joined

    @display(
        description=_("Hackathons Attended"),
        empty_value="0",
    )
    def display_hackathons(self, instance: Hacker):
        return instance.hackathons.count()


class HackathonLocationAdmin(ModelAdmin):
    list_display = (
        "name",
        "venue",
        "country",
    )
    search_fields = ("name", "venue", "country")


class CategoryAdmin(ModelAdmin):
    list_display = (
        "name",
        "color",
    )
    search_fields = ("name",)


class SchoolAdmin(ModelAdmin):
    list_display = (
        "name",
        "added_by",
        "public",
        "created_at",
    )
    search_fields = ("name", "added_by__username")
    list_filter = ("public",)


admin.site.site_header = "Hackathons Canada Admin"  # set header
admin.site.site_title = "Admin - Hackathons Canada"  # set title
admin.site.index_title = "Welcome to Hackathons Canada Admin Dashboard"

admin.site.register(Hacker, HackerAdmin)
admin.site.register(Hackathon, HackathonAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(HackathonLocation, HackathonLocationAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

if not app_settings.EMAIL_CONFIRMATION_HMAC:
    admin.site.unregister(EmailConfirmation)
    admin.site.register(EmailConfirmation, EmailConfirmationAdmin)

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin)

admin.site.unregister(Redirect)
admin.site.register(Redirect, RedirectAdmin)
