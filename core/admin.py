# Register your models here.
from allauth.account import app_settings
from django.contrib import admin
from django.contrib.auth.models import Group
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import Category, Hacker, Hackathon
from django.contrib.auth.admin import (
    UserAdmin as DjangoUserAdmin,
    GroupAdmin as BaseGroupAdmin,
)
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.db import models
from allauth.account.admin import (
    EmailConfirmationAdmin as BaseEmailConfirmation,
    EmailAddressAdmin as BaseEmailAddress,
)
from allauth.account.models import EmailAddress, EmailConfirmation


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
    search_fields = ("name", "location")

    def get_queryset(self, request):
        return self.model.objects.admin()


class HackerAdmin(DjangoUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
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


class CategoryAdmin(ModelAdmin):
    list_display = (
        "name",
        "color",
    )
    search_fields = ("name",)


admin.site.site_header = "Hackathons Canada Admin"  # set header
admin.site.site_title = "Admin - Hackathons Canada"  # set title
admin.site.index_title = "Welcome to Hackathons Canada Admin Dashboard"

admin.site.register(Hacker, HackerAdmin)
admin.site.register(Hackathon, HackathonAdmin)
admin.site.register(Category, CategoryAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

if not app_settings.EMAIL_CONFIRMATION_HMAC:
    admin.site.unregister(EmailConfirmation)
    admin.site.register(EmailConfirmation, EmailConfirmationAdmin)

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin)
