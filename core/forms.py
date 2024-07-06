from django import forms
from .models import Hackathon
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, HTML, Submit, Div

class HackathonForm(forms.ModelForm):
    name = forms.CharField(max_length=255)
    country = forms.CharField(max_length=255)
    city = forms.CharField(max_length=255)
    website = forms.URLField()
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
        super().__init__(self, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', wrapper_class='form-control'),
            Field('website', wrapper_class='form-control'),
            Field('country', wrapper_class='form-control'),
            Field('city', wrapper_class='form-control'),
            Field('start_date', wrapper_class='form-control'),
            Field('end_date', wrapper_class='form-control'),
            Field('start_time', wrapper_class='form-control'),
            Field('end_time', wrapper_class='form-control'),
            Field('application_deadline', wrapper_class='form-control'),
            Field('application_start_date', wrapper_class='form-control'),
            Field('min_age', wrapper_class='form-control'),
            Field('max_age', wrapper_class='form-control'),
            Field('category', wrapper_class='form-control'),
            Submit('submit', 'Submit', css_class='button white'),
           )

addHackathon = HackathonForm()
