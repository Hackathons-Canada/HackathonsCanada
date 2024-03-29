from django.urls import path

from . import views

urlpatterns = [
	path("", views.index, name="index"),
	path("hackathon/<str:current>", views.hackathon, name="hackathon"),
	path("landing", views.landing, name="landing"),
]
