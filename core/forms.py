from django import forms

from .models import Hackathon
from crispy_forms.helper import FormHelper  # type: ignore
from crispy_forms.layout import Layout, Field, HTML, Submit, Div, Fieldset


# make this dynamic
BIRTH_YEAR_CHOICES = ["2024", "2025"]


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
    min_education_level = forms.MultipleChoiceField()
    maximum_education_level = forms.MultipleChoiceField()
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
                "<h2 class = 'form-head-text py-2 mt-5 pt-5'>Feature Your Hackathon with Us.</h2>"
            ),
            HTML(
                "<h3 class = 'form-side-text mt-2 pb-2'>Let us help you promote your hackathon event.</h3>"
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
                HTML("<h2 class = 'form-side-text pt-5'>Banner</h2>"),
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
                "<h2 class = 'form-head-text pt-5 py-2'>Participant Info & Criteria</h2>"
            ),
            HTML(
                "<h2 class = 'form-side-text pb-2'>Define your criteria for the event’s participants.</h2>"
            ),
            Fieldset(
                "",  # this is for the legend
                Field("min_age"),
                Div(Field("minimum_education_level"), Field("numerical_prize_pool")),
            ),
            Submit(
                "submit",
                "Submit",
                css_class="py-2.5 px-5 me-2 mb-2 text-sm font-medium text-black focus:outline-none bg-white rounded-lg border border-black hover:bg-gray-700 hover:text-white focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700",
            ),
        )
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-button-style py-2"


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
