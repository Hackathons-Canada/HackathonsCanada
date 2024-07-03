from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("hackathons/", views.HackathonsPage.as_view(), name="hackathons"),
    path('add-hackathons/', views.addHackathons, name='add_hackathons'),
path('calendar/', views.calendar, name='calendar')
]
