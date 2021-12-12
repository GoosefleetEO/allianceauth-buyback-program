from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from allianceauth.authentication.models import CharacterOwnership

from ..models import Contract


@login_required
@permission_required("buybacks.basic_access")
def my_stats(request):

    values = {
        "outstanding": 0,
        "finished": 0,
    }

    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id"
    )

    contracts = Contract.objects.filter(
        issuer_id__in=characters,
    ).exclude(title__exact="")

    for contract in contracts:
        if contract.status == "outstanding":
            values["outstanding"] += contract.price
        if contract.status == "finished":
            values["finished"] += contract.price

    context = {
        "contracts": contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybacks.basic_access")
def program_stats(request, program_pk):
    contracts = Contract.objects.filter(
        program__pk=program_pk,
    )

    context = {
        "contracts": contracts,
        "mine": False,
    }

    return render(request, "buybackprogram/stats.html", context)
