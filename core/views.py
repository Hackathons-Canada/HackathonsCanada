import os
import random
from functools import cache
import json
from django.utils import timezone
from core.scraper import scrape_all
from django.http import HttpResponse, JsonResponse
from django_ratelimit.decorators import ratelimit
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import ListView


from .forms import (
    HackathonForm,
    NotificationPolicyForm,
    HackerSettingForm,
    CuratorRequestForm,
)
from django.shortcuts import redirect
from django.apps import apps

if apps.ready:
    from core.models import Hackathon, Hacker


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


@ratelimit(key="user_or_ip", rate="1/m", block=True)
def addHackathons(request):
    if request.method == "POST":
        form = HackathonForm(request.POST)
        if form.is_valid():
            return redirect("home")
    else:
        form = HackathonForm()
    return render(request, "hackathons/add_hackathon.html", {"form": form})


class HackathonsPage(ListView):
    template_name = "hackathons/hackathons.html"
    context_object_name = "hackathons"
    tdy_date = timezone.now()
    print(f"Current date and time: {tdy_date}")

    def get_queryset(self):
        tdy_date = timezone.now()
        print(f"Current date and time: {tdy_date}")
        try:
            render_type = self.kwargs["type"]
        except KeyError:
            render_type = "cards"
        if render_type == "calendar":
            data = Hackathon.objects.filter(end_date__gt=tdy_date)
            hackathonsList = []
            for hackathon in data:
                hackathonsList.append(
                    {
                        "title": f"{hackathon.name} - {hackathon.location.name}",
                        "start": hackathon.start_date.strftime("%Y-%m-%d"),
                        "end": hackathon.end_date.strftime("%Y-%m-%d"),
                        "url": hackathon.website,
                    }
                )
            return hackathonsList
        else:
            return Hackathon.objects.filter(end_date__gt=tdy_date)

    def get_context_data(
        self,
        **kwargs,
    ):
        context = super().get_context_data(**kwargs)
        try:
            render_type = self.kwargs["type"]
        except KeyError:
            render_type = "cards"
        if render_type == "list":
            context["type"] = "list"
        elif render_type == "calendar":
            context["type"] = "calendar"
            context["hackathonCalData"] = json.dumps(self.get_queryset())
        else:
            context["type"] = render_type
        return context


@login_required
def setting(request):
    hacker = Hacker.objects.get(id=request.user.id)
    notification_policy = hacker.notification_policy

    if request.method == "POST":
        form_setting = HackerSettingForm(instance=hacker)  # Initialize with instance
        form_notification = NotificationPolicyForm(
            instance=notification_policy
        )  # Initialize with instance

        if "form_setting_submit" in request.POST:
            form_setting = HackerSettingForm(request.POST, instance=hacker)
            if form_setting.is_valid():
                form_setting.save()
                return redirect("setting")
            else:
                print("Form Setting Errors:", form_setting.errors)
        elif "form_notification_submit" in request.POST:
            form_notification = NotificationPolicyForm(
                request.POST, instance=notification_policy
            )
            if form_notification.is_valid():
                form_notification.save()
                return redirect("setting")
            else:
                print("Form Notification Errors:", form_notification.errors)
    else:
        form_setting = HackerSettingForm(instance=hacker)
        form_notification = NotificationPolicyForm(instance=notification_policy)

    return render(
        request,
        "account/setting.html",
        {"form_setting": form_setting, "form_notification": form_notification},
    )


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
@ratelimit(key="user_or_ip", rate="1/m", block=True)
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
    return render(request, "curator/curator_request.html", {"form": form})


def curator_request_success(request):
    return render(request, "curator/curator_request_success.html")


class SavedHackathonsPage(ListView):
    template_name = "hackathons/saved_hackathons.html"
    context_object_name = "saved_hackathons"

    def get_queryset(self):
        user: Hacker = self.request.user
        return user.saved.all()


# checks if the user is an admin
def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
@ratelimit(key="user_or_ip", rate="1/d", block=True)
def scrape(request):
    scrape_all()
    return HttpResponse("Scraped!")
