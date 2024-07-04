import pandas as pd
from django.shortcuts import render
from django.views.generic import ListView
from core.models import Hackathon
from .forms import HackathonForm


def home(request):
    return render(request, "home.html")


def addHackathons(request):
    if request.method == "POST":
        form = HackathonForm(request.POST)
        if form.is_valid():
            return "form is valid, Nirek do smth here"
    else:
        form = HackathonForm()
    
    return render(request, "add_hackathon.html", {"form": form})


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
