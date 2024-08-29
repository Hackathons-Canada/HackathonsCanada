import os
import random
from functools import cache

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import ListView

from core.models import Hackathon, Hacker
from .forms import HackathonForm
from .forms import CuratorRequestForm

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
def save_hackathon(request: HttpRequest, hackathon_id):
    if request.method == "POST":
        hackathon = get_object_or_404(Hackathon, id=hackathon_id)
        hacker = get_object_or_404(Hacker, id=request.user.id)

        if hacker.saved.filter(id=hackathon_id).exists():
            return JsonResponse(
                {"status": "fail", "error": "Invalid request"}, status=400
            )

        hacker.saved.add(hackathon)
        return JsonResponse(
            {
                "status": "success",
                "hackathon": {
                    "id": hackathon.id,
                    "name": hackathon.name,
                },
            }
        )


@login_required
def unsave_hackathon(request: HttpRequest, hackathon_id):
    if request.method == "POST":
        hackathon = get_object_or_404(Hackathon, id=hackathon_id)
        hacker = get_object_or_404(Hacker, id=request.user.id)

        if not hacker.saved.filter(id=hackathon_id).exists():
            return JsonResponse(
                {"status": "fail", "error": "Invalid request"}, status=400
            )

        hacker.saved.remove(hackathon)
        return JsonResponse(
            {
                "status": "success",
                "hackathon": {
                    "id": hackathon.id,
                    "name": hackathon.name,
                },
            }
        )


@login_required
def request_curator_access(request):
    if request.method == "POST":
        form = CuratorRequestForm(request.POST)
        if form.is_valid():
            hackathon = form.cleaned_data["hackathon"]
            team_name = form.cleaned_data["team_name"]
            team_description = form.cleaned_data["team_description"]
            reason = form.cleaned_data["reason"]
            # Send an email to the hackathon organizers with the request
            # Django's email system?
            # just print the request to the console
            print(
                f"Request from {team_name} to be a curator for {hackathon}: {reason}. {team_name} description: {team_description}"
            )
            return redirect("curator_request_success")
    else:
        form = CuratorRequestForm()
    return render(request, "curator_request.html", {"form": form})


def curator_request_success(request):
    return render(request, "curator_request_success.html")


class SavedHackathonsPage(ListView):
    template_name = "saved_hackathons.html"
    context_object_name = "saved_hackathons"

    def get_queryset(self):
        user: Hacker = self.request.user
        return user.saved.all()
