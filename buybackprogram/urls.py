from django.conf.urls import url
from django.urls import path

from buybackprogram.views import calculate, common, programs, stats

app_name = "buybackprogram"

urlpatterns = [
    path("", common.index, name="index"),
    path("setup", programs.setup, name="setup"),
    path("program_add", programs.program_add, name="program_add"),
    url(
        r"^program/(?P<program_pk>[0-9]+)/edit_item$",
        programs.program_edit_item,
        name="program_edit_item",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/edit",
        programs.program_edit,
        name="program_edit",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/remove$",
        programs.program_remove,
        name="program_remove",
    ),
    url(
        r"^program/(?P<program_pk>[0-9]+)/calculate$",
        calculate.program_calculate,
        name="program_calculate",
    ),
    path("my_stats", stats.my_stats, name="my_stats"),
    path(
        "my_stats/<str:contract_title>/details/",
        stats.contract_details,
        name="contract_details",
    ),
    path("program_stats", stats.program_stats, name="program_stats"),
]
