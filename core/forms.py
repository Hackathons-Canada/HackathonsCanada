from django import forms
from .models import Hackathon
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Submit, Div, Fieldset



class HackathonForm(forms.ModelForm):
    short_name = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
    website = forms.URLField()
    country = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
   
    start_date = forms.DateTimeInput()
    end_date = forms.DateTimeInput()
    start_time = forms.DateTimeInput()
    end_time = forms.DateTimeInput()
    application_deadline = forms.DateTimeInput()
    application_start_date = forms.DateTimeInput()
    min_age = forms.IntegerField(min_value=0, max_value=100)
    max_age = forms.IntegerField(min_value=0, max_value=100)
    category = forms.MultipleChoiceField(required=False)
    
    class Meta:
        model = Hackathon
        exclude = ['created_at', 'updated_at', "source", "curators", "is_public", "notes", "metadata"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
            Field('name', css_class='form-control'),
            Field('website', css_class='form-control'),
            Field('country', css_class='form-control'),
            Field('city', css_class='form-control'),
            Field('start_date', css_class='form-control'),
            Field('end_date', css_class='form-control'),
            Field('start_time', css_class='form-control'),
            Field('end_time', css_class='form-control'),
            Field('application_deadline', css_class='form-control'),
            Field('application_start_date', css_class='form-control'),
            Field('min_age', css_class='form-control'),
            Field('max_age', css_class='form-control'),
            Field('category', css_class='form-control'),),
            Submit('submit', 'Submit', css_class='button white'),
           )

