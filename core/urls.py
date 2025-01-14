from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("hackathons/", views.HackathonListView.as_view(), name="hackathons"),
    path("add-hackathons/", views.addHackathons, name="add_hackathons"),
    path("setting/", views.setting, name="setting"),
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
    ),
    path(
        "hackathons/<int:hackathon_id>/save",
        views.save_hackathon,
        name="save_hackathon",
    ),
    path("hackathons/<int:hackathon_id>/vote/", views.handle_vote, name="handle_vote"),
    path("scrapeMlh/", views.scrapeMlh, name="scrapeMlh"),
    path("scrapeDevpost/", views.scrapeDevpost, name="scrapeDevpost"),
    path("scrapeEth/", views.scrapeEth, name="scrapeEth"),
    path("scrapeHackclub/", views.scrapeHackclub, name="scrapeHackclub"),
    path("export_cal/", views.calendar_generator, name="calendar_generator"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
