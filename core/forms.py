from django import forms
from .models import Hackathon
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Submit, Div, Fieldset,  Row, Column



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
        exclude = ['created_at', 'updated_at', "source", "curators", "is_public", "notes", "metadata"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML("<h2 class = 'pt-5'>Feature Your Hackathon with Us.</h2>"),
            HTML("<h3>Let us help you promote your hackathon event.</h3>"),
            Fieldset(
                Div(
                    Field('short_name', css_class='form-group'),
                    Field('short_name', css_class='form-group'),
                    css_class='form-group'
                    ),
                Div(
                    Field('country', css_class='form-control'),
                    Field('city', css_class='form-control'),
                    css_class='form-group'
                ),
                Field('website', css_class='form-control'),
                # To Do Make this look Better:
                Field('start_date', css_class='form-control'),
                Field('end_date', css_class='form-control'),
                ),
            Div(
                HTML("<img src = "" />"),
                HTML("<h2>Click to upload or drag and drop</h2>"),
                HTML("<h3>PNG or JPG (max. 800x400px)</h3>"),
                css_class='py-5'
                ),
            Fieldset(
                Field("image", css_class="form-control"),
                Field('application_start', css_class='form-control'),
                Field('application_deadline', css_class='form-control'), 
                ),
            HTML("<h2>Participant Info & Criteria</h2>"),
            HTML("<h2>Define your criteria for the event’s participants.</h2>"),
            Fieldset(
                Field('min_age', css_class='form-control'),
                Field('minimum_education_level', css_class='form-control'),
                Field('maximum_education_level', css_class='form-control'),
                Field('numerical_prize_pool', css_class='form-control'),
                ),
            Submit('submit', 'Submit', css_class='button white'),
           )

