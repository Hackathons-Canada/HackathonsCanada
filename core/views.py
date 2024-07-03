import pandas as pd
from django.shortcuts import render
from django.views.generic import ListView

from core.models import Hackathon


def home(request):
    return render(request, "home.html")


def addHackathons(request):
    context = {
        'title': 'Add a New Hackathon',
        'content': 'Use this form to add a new hackathon to the database.'
    }
    return render(request, '../templates/add_hackathon.html', context)


def calendar(request):
    context = {
        'title': 'Add a New Hackathon',
        'content': 'Use this form to add a new hackathon to the database.'
    }
    return render(request, '../templates/calendar.html', context)


class HackathonsPage(ListView):
    template_name = "hackathons.html"
    context_object_name = "hackathons"

    def get_queryset(self):
        return Hackathon.objects.all()
