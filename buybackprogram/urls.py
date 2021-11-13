from django.urls import path

from . import views

app_name = "buybackprogram"

urlpatterns = [
    path("", views.index, name="index"),
    path("setup", views.setup, name="setup"),
    path("program_add", views.program_add, name="program_add"),
]
