from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render

from allianceauth.authentication.models import CharacterOwnership

from ..models import Contract, ContractItem, Tracking, TrackingItem


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

    tracking_numbers = Tracking.objects.all().values_list("tracking_number")

    contracts = Contract.objects.filter(
        issuer_id__in=characters,
        title__in=tracking_numbers,
    )

    for contract in contracts:
        if contract.status == "outstanding":
            values["outstanding"] += contract.price
        if contract.status == "finished":
            values["finished"] += contract.price

        contract.items = ContractItem.objects.filter(contract=contract)

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

    return render(request, "buybackprogram/program_stats.html", context)


def contract_details(request, contract_title):

    try:

        notes = []

        contract = Contract.objects.get(title=contract_title)

        contract_items = ContractItem.objects.filter(contract=contract)

        tracking = Tracking.objects.get(
            tracking_number=contract_title,
        )

        tracking_items = TrackingItem.objects.filter(tracking=tracking)

        if contract.price != tracking.net_price:
            note = {
                "icon": "fa-skull-crossbones",
                "color": "alert-danger",
                "message": "Tracked price does not match contract price. You have either made an mistake in the tracking number or the contract price copy paste. Please remake contract.",
            }
            notes.append(note)

        context = {
            "notes": notes,
            "contract": contract,
            "contract_items": contract_items,
            "tracking": tracking,
            "tracking_items": tracking_items,
        }

        return render(request, "buybackprogram/contract_details.html", context)

    except Contract.DoesNotExist:
        return redirect("buybackprogram/stats.html")
