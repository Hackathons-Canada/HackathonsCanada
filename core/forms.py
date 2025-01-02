from django import forms
from django.db import OperationalError
from django.utils import timezone

from .models import (
    Hackathon,
    EDUCATION_CHOICES,
    HACKATHON_EDUCATION_CHOICES,
    Hacker,
    NotificationPolicy,
    School,
    CuratorRequest,
)
from django_countries.fields import CountryField
from crispy_forms.helper import FormHelper  # type: ignore
from crispy_forms.layout import Layout, Field, HTML, Submit, Div, Fieldset


class HackathonForm(forms.ModelForm):
    short_name = forms.CharField(max_length=255, required=False)
    name = forms.CharField(max_length=255)
    website = forms.URLField()
    country = CountryField(blank_label="(select country)").formfield(required=False)
    city = forms.CharField(max_length=255)
    image = forms.ImageField()
    start_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    application_start = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    application_deadline = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    min_age = forms.IntegerField(min_value=0, max_value=100, required=False)
    minimum_education_level = forms.ChoiceField(
        choices=HACKATHON_EDUCATION_CHOICES,
        widget=forms.Select,
        required=False,
        help_text="Select the minimum education level required to participate.",
    )
    maximum_education_level = forms.ChoiceField(
        choices=HACKATHON_EDUCATION_CHOICES,
        widget=forms.Select,
        required=False,
        help_text="Select the maximum education level required to participate.",
    )
    numerical_prize_pool = forms.IntegerField(min_value=0, required=False)
    category = forms.MultipleChoiceField(required=False)

    class Meta:
        model = Hackathon
        exclude = [
            "created_at",
            "updated_at",
            "source",
            "curators",
            "is_public",
            "notes",
            "metadata",
            "categories",
            "created_by",
            "hybrid",
            "net_vote",
            "notification_policy",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.layout = Layout(
            HTML(
                # Updated classes for better spacing and text styling
                "<h2 class='my-8 text-2xl font-semibold form-head-text'>Feature Your Hackathon with Us.</h2>"
            ),
            HTML(
                # Updated classes for better spacing and text styling
                "<h3 class='mb-6 text-lg font-normal form-side-text'>Let us help you promote your hackathon event.</h3>"
            ),
            Fieldset(
                "",
                Div(
                    Field("short_name"),
                    Field("name"),
                    # Use flex-row instead of flex-rows and fine-tune spacing
                    css_class="form-group-style flex flex-row gap-4",
                ),
                Field("website"),
                Div(
                    Field("country"),
                    Field("city"),
                    css_class="form-group-style flex flex-row gap-4",
                ),
                Div(
                    Field("start_date"),
                    Field("end_date"),
                    css_class="form-group-style flex flex-row gap-4",
                ),
            ),
            Div(
                HTML(
                    "<h2 class='mt-8 mb-4 text-xl font-semibold form-side-text'>Banner</h2>"
                ),
                HTML(
                    "<h2 class='form-upload-head mb-1'>Click to upload or drag and drop</h2>"
                ),
                HTML(
                    "<h3 class='form-upload-side text-sm text-gray-500'>PNG or JPG (max. 800x400px)</h3>"
                ),
                css_class="form-group-style",
            ),
            Fieldset(
                "",
                Field("image", css_class="form-control"),
                Field("application_start"),
                Field("application_deadline"),
            ),
            HTML(
                "<h2 class='my-8 text-2xl font-semibold form-head-text'>Participant Info & Criteria</h2>"
            ),
            HTML(
                "<h2 class='mb-4 text-lg font-normal form-side-text'>Define your criteria for the event’s participants.</h2>"
            ),
            Fieldset(
                "",
                Field("min_age"),
                Div(
                    Field("minimum_education_level"),
                    Field("maximum_education_level"),
                    Field("numerical_prize_pool"),
                ),
            ),
            Submit(
                "submit",
                "Submit",
                # Tweaked button styling for cleaner focus/hover states
                css_class=(
                    "py-3 px-6 mr-2 mb-2 text-sm font-medium "
                    "text-black bg-white border border-black rounded-lg "
                    "hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-4 focus:ring-gray-200 "
                    "dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 "
                    "dark:hover:bg-gray-700 dark:hover:text-white "
                    "dark:focus:ring-gray-700"
                ),
            ),
        )

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-button-style py-2"


class HackerSettingForm(forms.ModelForm):
    country = CountryField(blank_label="(select country)").formfield(required=False)
    city = forms.CharField(max_length=255, required=False)
    school = forms.ChoiceField(
        choices=(),
        widget=forms.Select,
        required=False,
        help_text="Select which school you attend.",
    )
    education = forms.ChoiceField(
        choices=EDUCATION_CHOICES, widget=forms.Select, required=False
    )

    username = forms.CharField(max_length=255, required=False)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=255, required=False)
    last_name = forms.CharField(max_length=255, required=False)
    birthday = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"}), required=False
    )
    personal_website = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Hacker
        exclude = [
            "objects",
            "saved",
            "is_active",
            "saved_categories",
            "email_preferences",
            "password",
            "date_joined",
        ]

    def set_school_choices(self):
        try:
            # Attempt to set the choices for the school field
            self.fields["school"].choices = (
                School.objects.filter(public=True).values_list("id", "name").all()
            )
        except OperationalError as e:
            self.fields["school"].choices = []  # Fallback to an empty list
            print(
                f"Error loading school choices: {e}, allowing empty list for this migration"
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_school_choices()
        temp_text_style: str = "border: 1px solid #ccc; border-radius: 8px; padding: 10px; width: 100%; box-sizing: border-box;"

        self.fields["email"].widget.attrs["disabled"] = True
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Main Heading
            HTML("<h1 class='text-3xl font-bold mb-6'>Profile Settings</h1>"),
            # General Profile Section
            Div(
                HTML("<h2 class='text-xl font-semibold mb-4'>General Profile</h2>"),
                Div(
                    Div(
                        Field(
                            "first_name",
                            css_class="form-control",
                            style=temp_text_style,
                        ),
                        Field(
                            "last_name", css_class="form-control", style=temp_text_style
                        ),
                        css_class="flex flex-row space-x-4",
                    ),
                    Div(
                        Field(
                            "country", css_class="form-control", style=temp_text_style
                        ),
                        Field("city", css_class="form-control", style=temp_text_style),
                        css_class="flex flex-row space-x-4",
                    ),
                    css_class="grouped-section p-6 rounded-lg mb-6",
                    style="background-color: rgba(255, 255, 255, 0.6); border-radius: 10px; padding: 24px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
                ),
            ),
            # Account Profile Section
            Div(
                HTML("<h2 class='text-xl font-semibold mb-4'>Account Profile</h2>"),
                Div(
                    Div(
                        Field(
                            "username", css_class="form-control", style=temp_text_style
                        ),
                        Field("email", css_class="form-control", style=temp_text_style),
                        css_class="flex flex-row space-x-4",
                    ),
                    Div(
                        Field(
                            "personal_website",
                            css_class="form-control",
                            style=temp_text_style,
                        ),
                        Field("birthday", css_class="form-control"),
                        css_class="flex flex-row space-x-4",
                    ),
                    css_class="grouped-section p-6 rounded-lg mb-6",
                    style="background-color: rgba(255, 255, 255, 0.6); border-radius: 10px; padding: 24px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);",
                ),
            ),
            # Education Profile
            Div(
                HTML("<h2 class='text-xl font-semibold mb-4'>Education Profile</h2>"),
                Div(
                    Field("school"),
                    Field("education"),
                    css_class="form-group-style",
                ),
            ),
            # Submit Button
            Submit(
                "form_setting_submit",
                "Save",
                css_class="py-3 px-6 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700",
            ),
        )

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-button-style py-2"


class NotificationPolicyForm(forms.ModelForm):
    radius_type = forms.ChoiceField(
        choices=[("km", "Kilometers"), ("mi", "Miles")],
        widget=forms.Select,
        required=False,
    )
    radius = forms.IntegerField(min_value=0, required=False)

    class Meta:
        model = NotificationPolicy
        fields = [
            "enabled",
            "weekly",
            "monthly",
            "added",
            "local_only",
            "only_eligible",
            "radius_type",
            "radius",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(
                '<h2 class="text-lg font-semibold mt-5 mb-2 form-head-text" style="font-size: 1.75rem;">Notification</h2>'
            ),
            Fieldset(
                "Get Notified via email for New Hackathons, based on your settings. (Does not work right now, comming soon)",
                Field("enabled"),
                Field("weekly"),
                Field("monthly"),
                Field("added"),
                Field("local_only"),
                Field("only_eligible"),
                Div(
                    Field("radius_type"),
                    Field("radius"),
                    css_class="form-group-style flex flex-rows space-x-4",
                ),
            ),
            Submit(
                "form_notification_submit",
                "Save",
                css_class="py-2.5 px-5 me-2 mb-2 text-sm font-medium text-black focus:outline-none bg-white rounded-lg border border-black hover:bg-gray-700 hover:text-white focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700",
            ),
        )


class CuratorRequestForm(forms.ModelForm):
    tdy_date = timezone.now()
    hackathon = forms.ModelChoiceField(
        queryset=Hackathon.objects.filter(end_date__gt=tdy_date, is_public=True),
        empty_label=None,
    )
    team_name = forms.CharField(label="Team/Organization Name")
    team_description = forms.CharField(
        label="Team/Organization Description", widget=forms.Textarea
    )
    reason = forms.CharField(
        label="Why do you want to be a curator for this hackathon?",
        widget=forms.Textarea,
    )

    class Meta:
        model = CuratorRequest
        exclude = ["created_by", "review_status", "reviewed_by"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hackathon"].widget.attrs.update(
            {
                "class": "form-control form-group-style flex flex-rows space-x-4 mt-2 mb-3"
            }
        )
        self.fields["team_name"].widget.attrs.update(
            {
                "class": "form-control form-group-style flex flex-rows space-x-4 mt-2 mb-3"
            }
        )
        self.fields["team_description"].widget.attrs.update(
            {
                "class": "form-control form-group-style flex flex-rows space-x-4 mt-2 mb-3"
            }
        )
        self.fields["reason"].widget.attrs.update(
            {
                "class": "form-control form-group-style flex flex-rows space-x-4 mt-2 mb-3"
            }
        )
