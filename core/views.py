from __future__ import annotations

import os
import random
from functools import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import transaction
from django.db.models import F, Q, Prefetch
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from icalendar import Calendar, Event

from core.models import Hackathon, Hacker, Vote, ReviewStatus
from core.scraper import scrape_all
from .forms import (
    HackathonForm,
    NotificationPolicyForm,
    HackerSettingForm,
    CuratorRequestForm,
)
from django.views.generic import ListView
from django.utils import timezone
from django.http import JsonResponse
from typing import Dict, Any


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


@ratelimit(key="user_or_ip", rate="4/m", block=True)
@login_required
@require_http_methods(["POST", "GET"])
def addHackathons(request):
    if request.method == "POST":
        form = HackathonForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            form.review_status = ReviewStatus.Pending
            form.created_by = Hacker.objects.get(id=request.user.id)
            form.save()
            return redirect("home")
    else:
        form = HackathonForm()
    return render(request, "hackathons/add_hackathon.html", {"form": form})


class HackathonListView(ListView):
    """
    A class-based view for displaying hackathons with efficient querying and filtering.
    Supports different view types (calendar, list, cards) and various filtering options.
    """

    template_name = "hackathons/hackathons.html"
    context_object_name = "hackathons"

    def get_queryset(self):
        """
        Build the queryset with all necessary filters and annotate vote status
        in a single efficient query.
        """
        # Base query with select_related to avoid n+1 queries
        queryset = Hackathon.objects.select_related("location").filter(
            end_date__gte=timezone.now(), is_public=True
        )

        # Apply filters based on query parameters
        filters = self._build_filters()
        if filters:
            queryset = queryset.filter(filters)

        # Annotate vote saved hackathons - James C - needs to be changed

        # Annotate vote status directly in the query instead of prefetching
        return Hackathon.annotate_user_data(queryset, self.request.user)

    def _build_filters(self) -> Q:
        """
        Build query filters based on request parameters.
        Returns a Q object combining all active filters.
        """
        filters = Q()
        params = self.request.GET

        country = params.get("country")
        if country and country != "none":
            if country == "World":
                filters &= ~Q(location__country="Online")
            else:
                filters &= Q(location__country=country)

        city = params.get("city")
        if city and city != "None":
            filters &= Q(location__name__icontains=city)

        start = params.get("start")
        if start and start != "None":
            filters &= Q(start_date__gte=start)

        end = params.get("end")
        if end and end != "None":
            filters &= Q(end_date__lte=end)

        return filters

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Prepare context data for the template, including calendar data if needed.
        """
        context = super().get_context_data(**kwargs)
        view_type = self.request.GET.get("view_type")

        # Add filter parameters to context
        context.update(
            {
                "type": view_type,
                "country": self.request.GET.get("country"),
                "city": self.request.GET.get("city"),
                "start": self.request.GET.get("start"),
                "end": self.request.GET.get("end"),
            }
        )

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

        elif "form_notification_submit" in request.POST:
            form_notification = NotificationPolicyForm(
                request.POST, instance=notification_policy
            )
            if form_notification.is_valid():
                form_notification.save()
                return redirect("setting")

    else:
        form_setting = HackerSettingForm(instance=hacker)
        form_notification = NotificationPolicyForm(instance=notification_policy)

    return render(
        request,
        "account/setting.html",
        {"form_setting": form_setting, "form_notification": form_notification},
    )


@login_required
@require_http_methods(["POST"])
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
                return JsonResponse({"status": "success", "hackathon": "removed"})

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
@ratelimit(key="user_or_ip", rate="4/m", block=True)
@require_http_methods(["POST", "GET"])
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
        """
        Build the queryset with all necessary filters and annotate vote status
        in a single efficient query.
        """
        user: Hacker = self.request.user

        queryset = user.saved.all()

        # Annotate vote status directly in the query instead of prefetching
        return Hacker.annotate_vote_status(queryset, self.request.user)

    def _annotate_user_data(self, queryset):
        """
        Efficiently annotate queryset with user-specific data using prefetch_related.
        """
        hacker = self.request.user

        # Prefetch votes in a single query, return True if the user has upvoted a post, null if no vote and False if downvoted

        votes_prefetch = Prefetch(
            "votes",
            queryset=Vote.objects.filter(hacker=hacker),
            to_attr="user_votes",
        )
        saved_prefetch = Prefetch(
            "interested_users",
            queryset=Hacker.objects.filter(id=hacker.id),
            to_attr="user_saved",
        )

        return queryset.prefetch_related(votes_prefetch, saved_prefetch)


# checks if the user is an admin
def is_admin(user: AbstractUser | AnonymousUser):
    return user.is_superuser


# fix this for v2


@login_required
@user_passes_test(is_admin)
def scrapeMlh(request):
    scrape_all(1)
    return HttpResponse("Scraped!")


@login_required
@user_passes_test(is_admin)
def scrapeDevpost(request):
    scrape_all(2)
    return HttpResponse("Scraped!")


@login_required
@user_passes_test(is_admin)
def scrapeEth(request):
    scrape_all(3)
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
    Handle voting for hackathons with improved error handling and atomic operations.
    Uses optimistic locking pattern to handle race conditions.
    """
    try:
        with transaction.atomic():
            hackathon = get_object_or_404(Hackathon, id=hackathon_id)
            hacker = request.user

            # Get current vote status with select_for_update to prevent race conditions
            current_vote = (
                Vote.objects.filter(hackathon=hackathon, hacker=hacker)
                .select_for_update()
                .first()
            )

            is_upvote = request.GET.get("vote_type") == "true"

            if request.method == "POST":
                if current_vote:
                    if current_vote.is_upvote == is_upvote:
                        return JsonResponse({"message": "Vote already exists"})

                    # Change vote direction
                    vote_diff = 2 if is_upvote else -2
                    current_vote.is_upvote = is_upvote
                    current_vote.save(update_fields=["is_upvote"])
                else:
                    # Create new vote
                    Vote.objects.create(
                        hackathon=hackathon, hacker=hacker, is_upvote=is_upvote
                    )
                    vote_diff = 1 if is_upvote else -1
            else:  # DELETE
                if not current_vote:
                    return JsonResponse({"message": "No vote found to remove"})

                vote_diff = -1 if current_vote.is_upvote else 1
                current_vote.delete()

            # Update net vote count
            Hackathon.objects.filter(id=hackathon_id).update(
                net_vote=F("net_vote") + vote_diff
            )

            return JsonResponse({"message": "Vote processed successfully"})

    except Exception as e:
        return JsonResponse(
            {"error": str(e) if settings.DEBUG else "An error occurred"}, status=500
        )
