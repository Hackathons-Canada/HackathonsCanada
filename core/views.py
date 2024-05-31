import pandas as pd
from django.shortcuts import render
from django.views.generic import ListView

from core.models import Hackathon


def home(request):
    return render(request, "home.html")

class HackathonsPage(ListView):
    template_name = "hackathons.html"
    context_object_name = "hackathons"
    def get_queryset(self):
        return Hackathon.objects.all()

