from django.conf.urls import url
from django.urls import path

from . import views

app_name = "buybackprogram"

urlpatterns = [
    path("", views.index, name="index"),
    path("setup", views.setup, name="setup"),
    path("program_add", views.program_add, name="program_add"),
    url(
        r"^program/(?P<program_pk>[0-9]+)/add_item$",
        views.program_add_item,
        name="program_add_item",
    ),
]
