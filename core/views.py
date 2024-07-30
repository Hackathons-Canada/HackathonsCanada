import os
import random
from functools import cache

from django.shortcuts import render
from django.views.generic import ListView

from core.models import Hackathon
from .forms import HackathonForm
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect


@cache
def get_images() -> list[str]:
    IMAGE_DIR = f"{settings.BASE_DIR}/static/assets/hackbanners"
    #  get all the image names in the directory
    return [f"assets/hackbanners/{img}" for img in os.listdir(IMAGE_DIR)]


def home(request):
    N_IMAGES = 10  # Number of images to be in the array
    image_names = get_images()
    shuffled_images = random.sample(image_names, N_IMAGES)
    # this splits the shuffled array in two halves
    left_images = shuffled_images[: N_IMAGES // 2]
    right_images = shuffled_images[N_IMAGES // 2 :]

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


@login_required
def save_hackathon(request, hackathon_id):
    if request.method == "POST":
        user = request.user
        hackathon = get_object_or_404(Hackathon, id=hackathon_id)
        user.saved.add(hackathon)

    return redirect("hackathons")


class SavedHackathonsPage(ListView):
    template_name = "saved_hackathons.html"
    context_object_name = "saved_hackathons"

    def get_queryset(self):
        user = self.request.user
        return user.saved.all()
