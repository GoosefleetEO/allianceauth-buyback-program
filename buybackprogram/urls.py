from django.conf.urls import url
from django.urls import path

from . import views

app_name = "buybackprogram"

urlpatterns = [
    path("", views.common.index, name="index"),
    path("setup", views.programs.setup, name="setup"),
    path("program_add", views.programs.program_add, name="program_add"),
    url(
        r"^program/(?P<program_pk>[0-9]+)/edit_item$",
        views.programs.program_edit_item,
        name="program_edit_item",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/edit",
        views.programs.program_edit,
        name="program_edit",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/calculate$",
        views.calculate.program_calculate,
        name="program_calculate",
    ),
]
