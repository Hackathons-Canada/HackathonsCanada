from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("hackathons/", views.HackathonsPage.as_view(), name="hackathons"),
    path("add-hackathons/", views.addHackathons, name="add_hackathons"),
    path("calendar/", views.calendar, name="calendar"),
    path(
        "saved_hackathons/",
        views.SavedHackathonsPage.as_view(),
        name="saved_hackathons",
    ),
    path(
        "request_curator_access/",
        views.request_curator_access,
        name="request_curator_access",
    ),
    path(
        "curator_request_success/",
        views.curator_request_success,
        name="curator_request_success",
      "hackathons/<int:hackathon_id>/save",
        views.save_hackathon,
        name="save_hackathon",
    ),
    path(
        "hackathons/<int:hackathon_id>/unsave",
        views.unsave_hackathon,
        name="unsave_hackathon",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
