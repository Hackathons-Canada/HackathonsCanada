from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("hackathons/", views.HackathonsPage.as_view(), name="hackathons"),
    path("add-hackathons/", views.addHackathons, name="add_hackathons"),
    path("calendar/", views.calendar, name="calendar"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)