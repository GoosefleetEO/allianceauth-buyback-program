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

    valid_contracts = []

    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    tracking_numbers = Tracking.objects.all()

    for tracking in tracking_numbers:

        contract = Contract.objects.filter(
            issuer_id__in=characters, title__contains=tracking.tracking_number
        ).first()

        if contract:

            contract.tracking = tracking

            logger.debug(
                "Contract %s has a match in tracking numbers" % contract.contract_id
            )

            if contract.status == "outstanding":
                values["outstanding"] += contract.price
                values["outstanding_count"] += 1
            if contract.status == "finished":
                values["finished"] += contract.price
                values["finished_count"] += 1

            contract.notes = []

            contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

            logger.debug("Issuer name for contract is %s" % contract.issuer_name)

            contract.items = ContractItem.objects.filter(contract=contract)

            if tracking.program:
                structure_id = tracking.program.location.structure_id
            else:
                structure_id = False

            if structure_id and structure_id != contract.start_location_id:
                note = {
                    "icon": "fa-compass",
                    "color": "red",
                    "message": "Contract location id %s does not match program location id %s"
                    % (contract.start_location_id, structure_id),
                }

                contract.notes.append(note)

            if tracking.net_price != contract.price:
                note = {
                    "icon": "fa-skull-crossbones",
                    "color": "red",
                    "message": "Tracked price does not match contract price. Either a mistake in the copy pasted values or seller has changed contracted items after calculating the price",
                }

                contract.note = note

            if not tracking.tracking_number == contract.title:
                note = {
                    "icon": "fa-exclamation",
                    "color": "orange",
                    "message": "Contract description contains extra characterse besides the tracking number. The description should be: '%s', instead it is: '%s'"
                    % (tracking.tracking_number, contract.title),
                }

                contract.notes.append(note)

            valid_contracts.append(contract)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def program_stats(request):

    valid_contracts = []

    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    logger.debug("Got characters for manager: %s" % characters)

    corporations = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__corporation_id", flat=True
    )

    logger.debug("Got corporations for manager: %s" % corporations)

    tracking_numbers = Tracking.objects.all()

    for tracking in tracking_numbers:

        contract = Contract.objects.filter(
            Q(assignee_id__in=characters) | Q(assignee_id__in=corporations),
            title__contains=tracking.tracking_number,
        ).first()

        if contract:

            contract.tracking = tracking

            logger.debug(
                "Contract %s has a match in tracking numbers" % contract.contract_id
            )

            if contract.status == "outstanding":
                values["outstanding"] += contract.price
                values["outstanding_count"] += 1
            if contract.status == "finished":
                values["finished"] += contract.price
                values["finished_count"] += 1

            contract.notes = []

            try:
                issuer_character = CharacterOwnership.objects.get(
                    character__character_id=contract.issuer_id
                )
                logger.debug(
                    "Got issuer character from auth: %s" % issuer_character.user
                )

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

            contract.assignee_name = EveEntity.objects.resolve_name(
                contract.assignee_id
            )

            contract.items = ContractItem.objects.filter(contract=contract)

            if tracking.program:
                structure_id = tracking.program.location.structure_id
            else:
                structure_id = False

            if structure_id and structure_id != contract.start_location_id:
                note = {
                    "icon": "fa-compass",
                    "color": "red",
                    "message": "Contract location id %s does not match program location id %s"
                    % (contract.start_location_id, structure_id),
                }

                contract.notes.append(note)

            if tracking.net_price != contract.price:
                note = {
                    "icon": "fa-skull-crossbones",
                    "color": "red",
                    "message": "Tracked price for %s does not match contract price. See details for more information"
                    % tracking.tracking_number,
                }

                contract.notes.append(note)

            if (
                contract.assignee_id in corporations
                and not tracking.program.is_corporation
            ):
                note = {
                    "icon": "fa-home",
                    "color": "orange",
                    "message": "Contract %s is made for your corporation while they should be made directly to your character in this program."
                    % tracking.tracking_number,
                }

                contract.notes.append(note)

            if tracking.program:
                if (
                    contract.assignee_id not in corporations
                    and tracking.program.is_corporation
                ):
                    note = {
                        "icon": "fa-user",
                        "color": "orange",
                        "message": "Contract %s is made for your character while they should be made to your corporation in this program."
                        % tracking.tracking_number,
                    }

                    contract.notes.append(note)

            if not tracking.tracking_number == contract.title:
                note = {
                    "icon": "fa-exclamation",
                    "color": "orange",
                    "message": "Contract description contains extra characterse besides the tracking number. The description should be: '%s', instead it is: '%s'"
                    % (tracking.tracking_number, contract.title),
                }

                contract.notes.append(note)

            valid_contracts.append(contract)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/program_stats.html", context)


@login_required
@permission_required("buybackprogram.see_all_statics")
def program_stats_all(request):

    valid_contracts = []

    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    tracking_numbers = Tracking.objects.all()

    for tracking in tracking_numbers:

        contract = Contract.objects.filter(
            title__contains=tracking.tracking_number
        ).first()

        if contract:

            contract.tracking = tracking

            logger.debug(
                "Contract %s has a match in tracking numbers" % contract.contract_id
            )

            if contract.status == "outstanding":
                values["outstanding"] += contract.price
                values["outstanding_count"] += 1
            if contract.status == "finished":
                values["finished"] += contract.price
                values["finished_count"] += 1

            contract.notes = []

            try:
                issuer_character = CharacterOwnership.objects.get(
                    character__character_id=contract.issuer_id
                )
                logger.debug(
                    "Got issuer character from auth: %s" % issuer_character.user
                )

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

            contract.assignee_name = EveEntity.objects.resolve_name(
                contract.assignee_id
            )

            contract.items = ContractItem.objects.filter(contract=contract)

            if tracking.program:
                structure_id = tracking.program.location.structure_id
            else:
                structure_id = False

            if structure_id and structure_id != contract.start_location_id:
                note = {
                    "icon": "fa-compass",
                    "color": "red",
                    "message": "Contract location id %s does not match program location id %s"
                    % (contract.start_location_id, structure_id),
                }

                contract.notes.append(note)

            if tracking.net_price != contract.price:
                note = {
                    "icon": "fa-skull-crossbones",
                    "color": "red",
                    "message": "Tracked price for %s does not match contract price. See details for more information"
                    % tracking.tracking_number,
                }

                contract.notes.append(note)

            if not tracking.tracking_number == contract.title:
                note = {
                    "icon": "fa-exclamation",
                    "color": "orange",
                    "message": "Contract description contains extra characterse besides the tracking number. The description should be: '%s', instead it is: '%s'"
                    % (tracking.tracking_number, contract.title),
                }

                contract.notes.append(note)

            valid_contracts.append(contract)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/program_stats_all.html", context)


@login_required
@permission_required("buybackprogram.basic_access")
def contract_details(request, contract_title):
    try:

        notes = []

        contract = Contract.objects.get(title__contains=contract_title)

        contract_items = ContractItem.objects.filter(contract=contract)

        tracking = Tracking.objects.get(
            tracking_number=contract_title,
        )

        tracking_items = TrackingItem.objects.filter(tracking=tracking)

        contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)
        contract.assignee_name = EveEntity.objects.resolve_name(contract.assignee_id)

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
