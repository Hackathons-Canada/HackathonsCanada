from django import forms
from .models import (
    Hackathon,
    HACKATHON_EDUCATION_CHOICES,
    Hacker,
    NotificationPolicy,
    School,
)
from django_countries.fields import CountryField
from crispy_forms.helper import FormHelper  # type: ignore
from crispy_forms.layout import Layout, Field, HTML, Submit, Div, Fieldset


class HackathonForm(forms.ModelForm):
    short_name = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
    website = forms.URLField()
    country = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    image = forms.ImageField()
    start_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    application_start = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    application_deadline = forms.DateField(
        widget=forms.TextInput(attrs={"type": "date"})
    )
    min_age = forms.IntegerField(min_value=0, max_value=100)
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
    numerical_prize_pool = forms.IntegerField(min_value=0)
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
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML(
                "<h2 class = 'py-2 pt-5 mt-5 form-head-text'>Feature Your Hackathon with Us.</h2>"
            ),
            HTML(
                "<h3 class = 'pb-2 mt-2 form-side-text'>Let us help you promote your hackathon event.</h3>"
            ),
            Fieldset(
                "",
                Div(
                    Field("short_name"),
                    Field("name"),
                    css_class="form-group-style flex flex-rows space-x-4",
                ),
                Field("website"),
                Div(
                    Field("country"),
                    Field("city"),
                    css_class="form-group-style flex flex-rows space-x-4",
                ),
                # To Do Make this look Better:
                Div(
                    Field("start_date"),
                    Field("end_date"),
                    css_class="form-group-style flex flex-rows space-x-4",
                ),
            ),
            Div(
                HTML("<h2 class = 'pt-5 form-side-text'>Banner</h2>"),
                HTML(
                    "<h2 class = 'form-upload-head'>Click to upload or drag and drop</h2>"
                ),
                HTML("<h3 class = 'form-upload-side'>PNG or JPG (max. 800x400px)</h3>"),
                css_class="form-group-style",
            ),
            Fieldset(
                "",  # this is for the legend
                Field("image", css_class="form-control"),
                Field("application_start"),
                Field("application_deadline"),
            ),
            HTML(
                "<h2 class = 'py-2 pt-5 form-head-text'>Participant Info & Criteria</h2>"
            ),
            HTML(
                "<h2 class = 'pb-2 form-side-text'>Define your criteria for the event’s participants.</h2>"
            ),
            Fieldset(
                "",  # this is for the legend
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
                css_class="py-2.5 px-5 me-2 mb-2 text-sm font-medium text-black focus:outline-none bg-white rounded-lg border border-black hover:bg-gray-700 hover:text-white focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700",
            ),
        )
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-button-style py-2"


class HackerSettingForm(forms.ModelForm):
    country = CountryField(blank_label="(select country)").formfield()
    city = forms.CharField(max_length=255)
    school = forms.ChoiceField(
        choices=School.objects.all(),
        widget=forms.Select,
        required=False,
        help_text="Select which school you attend.",
    )
    education = forms.ChoiceField(
        choices=HACKATHON_EDUCATION_CHOICES, widget=forms.Select
    )
    username = forms.CharField(max_length=255)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=255)
    last_name = forms.CharField(max_length=255)
    birthday = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    personal_website = forms.CharField(max_length=255, required=False)

    class Meta:
        model = Hacker
        exclude = ["objects", "saved", "saved_categories", "notification_policy"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML("<h2 class = 'py-2 pt-5 mt-5 form-head-text'>Profile.</h2>"),
            Fieldset(
                "NOtification Settings",
                Div(
                    HTML("<h3 class = 'pb-2 mt-2 form-side-text'>General.</h3>"),
                    Div(
                        Field("first_name"),
                        Field("last_name"),
                        css_class="form-group-style flex flex-rows space-x-4",
                    ),
                    Div(
                        Field("country"),
                        Field("city"),
                        css_class="form-group-style flex flex-rows space-x-4",
                    ),
                    HTML(
                        "<h3 class = 'pb-2 mt-2 form-side-text'>Account Profile.</h3>"
                    ),
                    Div(
                        Field("username"),
                        Field("email"),
                        css_class="form-group-style flex flex-rows space-x-4",
                    ),
                    Div(
                        Field("personal_website"),
                        Field("birthday"),
                        css_class="form-group-style flex flex-rows space-x-4",
                    ),
                    Div(
                        HTML("<h3 class = 'form-upload-side'>Education Profile</h3>"),
                        Field("school"),
                        Field("education"),
                        css_class="form-group-style",
                    ),
                ),
            ),
            Submit(
                "save",
                "Save",
                css_class="py-2.5 px-5 me-2 mb-2 text-sm font-medium text-black focus:outline-none bg-white rounded-lg border border-black hover:bg-gray-700 hover:text-white focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700",
            ),
        )
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-button-style py-2"


class NotificationPolicyForm(forms.ModelForm):
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
            Fieldset(
                "Notification Settings",
                Field("enabled"),
                Field("weekly"),
                Field("monthly"),
                Field("added"),
                Field("local_only"),
                Field("only_eligible"),
                Field("radius_type"),
                Field("radius"),
            ),
            Submit(
                "save",
                "Save",
                css_class="py-2.5 px-5 me-2 mb-2 text-sm font-medium text-black focus:outline-none bg-white rounded-lg border border-black hover:bg-gray-700 hover:text-white focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700",
            ),
        )


class CuratorRequestForm(forms.Form):
    hackathon = forms.CharField(label="Hackathon")
    team_name = forms.CharField(label="Team/Organization Name")
    team_description = forms.CharField(
        label="Team/Organization Description", widget=forms.Textarea
    )
    reason = forms.CharField(
        label="Why do you want to be a curator for this hackathon?",
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hackathon"].widget.attrs.update({"class": "form-control"})
        self.fields["team_name"].widget.attrs.update({"class": "form-control"})
        self.fields["team_description"].widget.attrs.update({"class": "form-control"})
        self.fields["reason"].widget.attrs.update({"class": "form-control"})
