from django import forms
from .models import Hackathon


class HackathonForm(forms.ModelForm):
    class Meta:
        model = Hackathon
        fields = ['name', 'start_date', 'end_date', 'location', 'url', 'fgimage', 'bgimage']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }