from django import forms
from .models import Hackathon


class HackathonForm(forms.ModelForm):
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
        
