from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import render
from eveuniverse.models import EveSolarSystem, EveType

from allianceauth.services.hooks import get_extension_logger

from buybackprogram.models import Program

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.basic_access")
def index(request):

    user_groups = request.user.groups.all()

    logger.debug("User %s has groups: %s" % (request.user, user_groups))

    user_state = [request.user.profile.state]

    logger.debug("User %s state is : %s" % (request.user, user_state))

    program = (
        Program.objects.filter(
            Q(restricted_to_group__in=request.user.groups.all())
            | Q(restricted_to_group__isnull=True)
            | Q(owner__user=request.user)
        )
        .filter(
            Q(restricted_to_state=request.user.profile.state)
            | Q(restricted_to_state__isnull=True)
            | Q(owner__user=request.user)
        )
        .distinct()
    )

    context = {"programs": program}

    return render(request, "buybackprogram/index.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def item_autocomplete(request):
    items = EveType.objects.filter(published=True).exclude(
        eve_group__eve_category__id=9
    )

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
