from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
import os
import random
from functools import cache
import json
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from silk.profiling.profiler import silk_profile

from core.scraper import scrape_all
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import ListView
from django.shortcuts import redirect
from django.db.models import Q
from icalendar import Calendar, Event
from django_ratelimit.decorators import ratelimit


from core.models import Hackathon, Hacker, Vote, ReviewStatus

from .forms import (
    HackathonForm,
    NotificationPolicyForm,
    HackerSettingForm,
    CuratorRequestForm,
)


@cache
def get_images() -> list[str]:
    IMAGE_DIR = f"{settings.BASE_DIR}/static/assets/hackbanners"
    #  get all the image names in the directory
    # todo: reimpl using static()
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


# @ratelimit(key="user_or_ip", rate="1/m", block=True)
def addHackathons(request):
    if request.method == "POST":
        form = HackathonForm(request.POST)
        if form.is_valid():
            print("sending the form")
            form.save(commit=False)
            form.review_status = ReviewStatus.Pending
            form.created_by = Hacker.objects.get(id=request.user.id)
            form.save()
            return redirect("home")
    else:
        form = HackathonForm()
    return render(request, "hackathons/add_hackathon.html", {"form": form})


def hackathon_page(request):
    tdy_date = timezone.now()

    hacker = Hacker.objects.filter(id=request.user.id).first()

    view_type = request.GET.get("view_type")
    country = request.GET.get("country")
    city = request.GET.get("city")
    start = request.GET.get("start")
    end = request.GET.get("end")

    query_base = Q(end_date__gte=tdy_date, is_public=True)
    if country and country != "none" and country != "World":
        query_base &= Q(location__country=country)
    elif country == "World":
        query_base &= ~Q(location__country="Online")

    if city and city != "None":
        print(city)
        query_base &= Q(location__name__icontains=city)

    if start and start != "None":
        query_base &= Q(start_date__gte=start)

    if end and end != "None":
        query_base &= Q(end_date__lte=end)

    upcoming_hackathons = Hackathon.objects.filter(query_base)

    if view_type == "calendar":
        hackathonsList = []
        for hackathon in upcoming_hackathons:
            hackathonsList.append(
                {
                    "title": f"{hackathon.name} - {hackathon.location.name}",
                    "start": hackathon.start_date.strftime("%Y-%m-%d"),
                    "end": hackathon.end_date.strftime("%Y-%m-%d"),
                    "url": hackathon.website,
                }
            )
        context = {
            "hackathons": json.dumps(hackathonsList),
            "type": view_type,
            "country": country,
            "city": city,
            "start": start,
            "end": end,
        }
        return render(request, "hackathons/hackathons.html", context)
    else:
        hackathon_with_user_info = []

        if hacker is not None:
            user_votes = Vote.objects.filter(hacker=request.user.id)
            saved = hacker.saved.values_list("id", flat=True).values_list(
                "id", flat=True
            )
            for hackathon in upcoming_hackathons:
                vote_data = user_votes.filter(hackathon=hackathon).first()
                setattr(
                    hackathon,
                    "vote_state",
                    vote_data.is_upvote if vote_data is not None else None,
                )
                setattr(
                    hackathon,
                    "user_saved",
                    True if saved.filter(id=hackathon.id).exists() else False,
                )

                hackathon_with_user_info.append(hackathon)
        else:
            hackathon_with_user_info = upcoming_hackathons

        context = {
            "hackathons": hackathon_with_user_info,
            "type": view_type,
            "country": country,
            "city": city,
            "start": start,
            "end": end,
        }

        return render(request, "hackathons/hackathons.html", context)


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
        page_type = request.GET.get("page_type")

        if hacker.saved.filter(id=hackathon_id).exists():
            hacker.saved.remove(hackathon)
            if page_type == "saved":
                return redirect("saved_hackathons")
            else:
                return JsonResponse({"status": "sucess", "hackathon": "removed"})

        hacker.saved.add(hackathon)
        if page_type == "saved":
            return redirect("saved_hackathons")
        else:
            return JsonResponse(
                {
                    "status": "success",
                    "hackathon": {
                        "id": hackathon.id,
                        "name": hackathon.name,
                    },
                }
            )


def str_to_bool(s):
    return s.lower() in ["true", "1", "yes"]


@login_required
@ratelimit(key="user_or_ip", rate="1/m", block=True)
def request_curator_access(request):
    if request.method == "POST":
        form = CuratorRequestForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.review_status = ReviewStatus.Pending
            form.created_by = Hacker.objects.get(id=request.user.id)
            form.save()

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
def is_admin(user: AbstractUser | AnonymousUser):
    return user.is_superuser


@login_required
@user_passes_test(is_admin)
@silk_profile(name="scrape_all")
def scrape(request):
    scrape_all()  # todo: add a celery task to scrape/make async
    return HttpResponse("Scraped!")


@cache_page(60 * 60)  # 1 hour cache
def calendar_generator(request):
    tdy_date = timezone.now()
    country = request.GET.get("country")
    city = request.GET.get("city")
    start = request.GET.get("start")
    end = request.GET.get("end")

    query_base = Q(end_date__gte=tdy_date, is_public=True)
    if country and country != "none" and country != "World":
        query_base &= Q(location__country=country)
    elif country == "World":
        query_base &= ~Q(location__country="Online")

    if city and city != "None":
        print(city)
        query_base &= Q(location__name__icontains=city)

    if start and start != "None":
        query_base &= Q(start_date__gte=start)

    if end and end != "None":
        query_base &= Q(end_date__lte=end)

    upcoming_hackathons = Hackathon.objects.filter(query_base)
    cal = Calendar()
    for hackathon in upcoming_hackathons:
        ical_event = Event()
        ical_event.add("summary", hackathon.name)
        ical_event.add("dtstart", hackathon.start_date)
        ical_event.add("dtend", hackathon.end_date)
        ical_event.add("location", hackathon.location.name)
        ical_event.add("uid", hackathon.duplication_id)
        cal.add_component(ical_event)
    response = HttpResponse(cal.to_ical(), content_type="text/calendar")
    response["Content-Disposition"] = "attachment; filename=hackathons.ics"
    return response


@login_required
@require_http_methods(["POST", "DELETE"])
@ratelimit(key="user_or_ip", rate="30/m", block=True)
def handle_vote(request, hackathon_id):
    """
    Handle voting for hackathons.
    POST: Create or update vote
    DELETE: Remove vote
    """
    try:
        with transaction.atomic():
            hackathon = get_object_or_404(Hackathon, id=hackathon_id)
            hacker = get_object_or_404(Hacker, id=request.user.id)

            if request.method == "POST":
                is_upvote = request.GET.get("vote_type") == "upvote"

                # Check for existing vote
                existing_vote = (
                    Vote.objects.filter(hackathon=hackathon, hacker=hacker)
                    .select_for_update()
                    .first()
                )

                if existing_vote:
                    if existing_vote.is_upvote == is_upvote:
                        return JsonResponse(
                            {
                                "message": "Vote already exists",
                            }
                        )

                    vote_diff = (
                        2 if is_upvote else -2
                    )  # Switching from down to up or vice versa
                    existing_vote.is_upvote = is_upvote
                    existing_vote.time_created = timezone.now()
                    existing_vote.save(update_fields=["is_upvote", "time_created"])

                else:
                    Vote.objects.create(
                        hackathon=hackathon, hacker=hacker, is_upvote=is_upvote
                    )
                    vote_diff = 1 if is_upvote else -1

                hackathon = (
                    Hackathon.objects.filter(id=hackathon_id).select_for_update().get()
                )
                hackathon.net_vote = F("net_vote") + vote_diff
                hackathon.save(update_fields=["net_vote"])

                return JsonResponse(
                    {
                        "message": "Vote recorded successfully",
                    }
                )

            elif request.method == "DELETE":
                # Remove vote if exists
                vote = (
                    Vote.objects.filter(hackathon=hackathon, hacker=hacker)
                    .select_for_update()
                    .first()
                )

                if vote:
                    vote_diff = -1 if vote.is_upvote else 1
                    vote.delete()

                    # Update net_vote atomically
                    hackathon = (
                        Hackathon.objects.filter(id=hackathon_id)
                        .select_for_update()
                        .update(net_vote=F("net_vote") + vote_diff)
                    )
                    hackathon.save(update_fields=["net_vote"])
                    return JsonResponse(
                        {
                            "message": "Vote removed successfully",
                        }
                    )

                return JsonResponse(
                    {
                        "message": "No vote found to remove",
                    }
                )

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception:
        return JsonResponse(
            {"error": "An error occurred while processing your vote"}, status=500
        )
