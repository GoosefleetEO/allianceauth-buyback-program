from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import redirect, render
from eveuniverse.models import EveEntity

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.services.hooks import get_extension_logger

from ..models import Contract, ContractItem, Tracking, TrackingItem

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.basic_access")
def my_stats(request):

    values = {
        "outstanding": 0,
        "finished": 0,
    }

    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    tracking = Tracking.objects.all()

    tracking_numbers = tracking.values_list("tracking_number", flat=True)

    contracts = Contract.objects.filter(
        issuer_id__in=characters,
        title__in=tracking_numbers,
    )

    for contract in contracts:

        if contract.status == "outstanding":
            values["outstanding"] += contract.price
        if contract.status == "finished":
            values["finished"] += contract.price

        contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

        contract.items = ContractItem.objects.filter(contract=contract)

        contract_tracking = tracking.filter(tracking_number=contract.title).first()

        if contract_tracking.net_price != contract.price:
            note = {
                "icon": "fa-skull-crossbones",
                "color": "red",
                "message": "Tracked price does not match contract price. Either a mistake in the copy pasted values or seller has changed contracted items after calculating the price",
            }

            contract.note = note

    context = {
        "contracts": contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def program_stats(request):

    values = {
        "outstanding": 0,
        "finished": 0,
    }

    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    logger.debug("Got characters for manager: %s" % characters)

    corporations = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__corporation_id", flat=True
    )

    logger.debug("Got corporations for manager: %s" % corporations)

    tracking = Tracking.objects.all()

    tracking_numbers = tracking.values_list("tracking_number", flat=True)

    contracts = Contract.objects.filter(
        Q(assignee_id__in=characters) | Q(assignee_id__in=corporations),
        title__in=tracking_numbers,
    )

    logger.debug("Got contracts for manager: %s" % contracts)

    for contract in contracts:

        if contract.status == "outstanding":
            values["outstanding"] += contract.price
        if contract.status == "finished":
            values["finished"] += contract.price

        contract.notes = []

        try:
            issuer_character = CharacterOwnership.objects.get(
                character__character_id=contract.issuer_id
            )
            logger.debug("Got issuer character from auth: %s" % issuer_character.user)

        except CharacterOwnership.DoesNotExist:
            issuer_character = False
            logger.debug("Contract issuer not registered on AUTH")

            note = {
                "icon": "fa-question",
                "color": "orange",
                "message": "Issuer not registered on AUTH. Possibly an unregistered alt.",
            }

            contract.notes.append(note)

        contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

        contract.assignee_name = EveEntity.objects.resolve_name(contract.assignee_id)

        contract.items = ContractItem.objects.filter(contract=contract)

        contract_tracking = tracking.filter(tracking_number=contract.title).first()

        if contract_tracking.net_price != contract.price:
            note = {
                "icon": "fa-skull-crossbones",
                "color": "red",
                "message": "Tracked price for %s does not match contract price. See details for more information"
                % contract_tracking.tracking_number,
            }

            contract.notes.append(note)

        if (
            contract.assignee_id in corporations
            and not contract_tracking.program.is_corporation
        ):
            note = {
                "icon": "fa-home",
                "color": "orange",
                "message": "Contract %s is made for your corporation while they should be made directly to your character in this program."
                % contract_tracking.tracking_number,
            }

            contract.notes.append(note)

        if (
            contract.assignee_id not in corporations
            and contract_tracking.program.is_corporation
        ):
            note = {
                "icon": "fa-user",
                "color": "orange",
                "message": "Contract %s is made for your character while they should be made to your corporation in this program."
                % contract_tracking.tracking_number,
            }

            contract.notes.append(note)

    context = {
        "contracts": contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/program_stats.html", context)


@login_required
@permission_required("buybackprogram.manage_all_programs")
def program_stats_all(request):

    values = {
        "outstanding": 0,
        "finished": 0,
    }

    tracking = Tracking.objects.all()

    tracking_numbers = tracking.values_list("tracking_number", flat=True)

    contracts = Contract.objects.filter(
        title__in=tracking_numbers,
    )

    for contract in contracts:

        if contract.status == "outstanding":
            values["outstanding"] += contract.price
        if contract.status == "finished":
            values["finished"] += contract.price

        contract.notes = []

        try:
            issuer_character = CharacterOwnership.objects.get(
                character__character_id=contract.issuer_id
            )
            logger.debug("Got issuer character from auth: %s" % issuer_character.user)

        except CharacterOwnership.DoesNotExist:
            issuer_character = False
            logger.debug("Contract issuer not registered on AUTH")

            note = {
                "icon": "fa-question",
                "color": "orange",
                "message": "Issuer not registered on AUTH. Possibly an unregistered alt.",
            }

            contract.notes.append(note)

        contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

        contract.assignee_name = EveEntity.objects.resolve_name(contract.assignee_id)

        contract.items = ContractItem.objects.filter(contract=contract)

        contract_tracking = tracking.filter(tracking_number=contract.title).first()

        if contract_tracking.net_price != contract.price:
            note = {
                "icon": "fa-skull-crossbones",
                "color": "red",
                "message": "Tracked price for %s does not match contract price. See details for more information"
                % contract_tracking.tracking_number,
            }

            contract.notes.append(note)

    context = {
        "contracts": contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/program_stats_all.html", context)


@login_required
@permission_required("buybackprogram.basic_access")
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
