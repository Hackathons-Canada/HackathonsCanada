from django import forms
from .models import Hackathon
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Submit, Div, Fieldset, Row, Column


class HackathonForm(forms.ModelForm):
    short_name = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
    website = forms.URLField()
    country = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    image = forms.ImageField()
    start_date = forms.DateTimeInput()
    end_date = forms.DateTimeInput()
    application_start = forms.DateTimeInput()
    application_deadline = forms.DateTimeInput()
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
                "<h2 class = 'form-head-text py-2 pt-5'>Feature Your Hackathon with Us.</h2>"
            ),
            HTML(
                "<h3 class = 'form-side-text pb-2'>Let us help you promote your hackathon event.</h3>"
            ),
            Fieldset(
                "",
                Div(
                    "general info",
                    Field("short_name"),
                    Field("name"),
                    css_class="form-group-style",
                ),
                Div(Field("country"), Field("city"), css_class="form-group-style"),
                Field("website"),
                # To Do Make this look Better:
                Field("start_date"),
                Field("end_date"),
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
                Field("minimum_education_level"),
                Field("maximum_education_level"),
                Field("numerical_prize_pool"),
            ),
            Submit("submit", "Submit", css_class="button white py-5"),
        )
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-button-style py-2"
