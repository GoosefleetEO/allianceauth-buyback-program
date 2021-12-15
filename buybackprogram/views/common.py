from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render
from eveuniverse.models import EveSolarSystem, EveType

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import Program

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.basic_access")
def index(request):
    context = {"programs": Program.objects.filter()}

    return render(request, "buybackprogram/index.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def item_autocomplete(request):
    items = EveType.objects.all()

    q = request.GET.get("q", None)

    if q is not None:
        items = items.filter(name__icontains=q)

    items = items.annotate(
        value=F("id"),
        text=F("name"),
    ).values("value", "text")

    return JsonResponse(list(items), safe=False)


@login_required
@permission_required("buybackprogram.manage_programs")
def solarsystem_autocomplete(request):
    items = EveSolarSystem.objects.all()

    q = request.GET.get("q", None)

    if q is not None:
        items = items.filter(name__icontains=q)

    items = items.annotate(
        value=F("id"),
        text=F("name"),
    ).values("value", "text")

    return JsonResponse(list(items), safe=False)
