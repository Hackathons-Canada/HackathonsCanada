from django.shortcuts import render
from django.views.generic import ListView
from core.models import Hackathon
from .forms import HackathonForm

import random


def home(request):
    image_names = [
        "uft.png",
        "cal.png",
        "delta.png",
        "form.png",
        "gt.png",
        "har.png",
        "hawk.png",
        "la.png",
        "mit.png",
        "north.png",
        "ryth.png",
        "tree.png",
    ]

    shuffled_images = random.sample(image_names, len(image_names))

    # this splits the shuffled array in two halves
    midpoint = len(shuffled_images) // 2
    left_images = shuffled_images[:midpoint]
    right_images = shuffled_images[midpoint:]

    context = {
        "left_images": left_images,
        "right_images": right_images,
    }

    return render(request, "home.html", context)


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
        "title": "Add a New Hackathon",
        "content": "Use this form to add a new hackathon to the database.",
    }
    return render(request, "../templates/calendar.html", context)


class HackathonsPage(ListView):
    template_name = "hackathons.html"
    context_object_name = "hackathons"

    def get_queryset(self):
        return Hackathon.objects.all()
