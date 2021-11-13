from django.urls import path

from . import views

app_name = "buybackprogram"

urlpatterns = [
    path("", views.index, name="index"),
]
