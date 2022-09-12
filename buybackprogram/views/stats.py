import json
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from eveuniverse.models import EveEntity
from datetime import datetime

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.notes import (
    note_missing_from_contract,
    note_missing_from_tracking,
    note_quantity_missing_from_contract,
    note_quantity_missing_from_tracking,
)

from ..models import (
    Contract,
    ContractItem,
    ContractNotification,
    Tracking,
    TrackingItem,
)

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.basic_access")
def my_stats(request):

    # List for valid contracts to be displayed
    valid_contracts = []

    # Tracker values
    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    # Request user owned characters
    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    # Get all tracking objects that have a linked contract to them for the user
    tracking_numbers = (
        Tracking.objects.filter(contract__isnull=False)
        .filter(contract__issuer_id__in=characters)
        .filter(contract__date_expired__gte=timezone.now())
        .prefetch_related("contract")
    )

    # Loop tracking objects to see if we have any contracts
    for tracking in tracking_numbers:

        # Get notes for this contract
        tracking.contract.notes = ContractNotification.objects.filter(
            contract=tracking.contract
        )

        # Walk the tracker values for contracts
        if tracking.contract.status == "outstanding":
            values["outstanding"] += tracking.contract.price
            values["outstanding_count"] += 1
        if tracking.contract.status == "finished":
            values["finished"] += tracking.contract.price
            values["finished_count"] += 1

        # Get the name for the issuer
        tracking.contract.issuer_name = EveEntity.objects.resolve_name(
            tracking.contract.issuer_id
        )

        # Get the name for the assignee
        tracking.contract.assignee_name = EveEntity.objects.resolve_name(
            tracking.contract.assignee_id
        )

        # Add contract to the valid contract list
        valid_contracts.append(tracking)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.basic_access")
def program_performance(request, program_pk):
    # Tracker values
    monthstats = {
            "status": {},
            "isk": {},
            "n": {},
            "items": {},
            "users": {},
    }

    # Get all tracking objects that have a linked contract to them for the user
    tracking_numbers = (
        Tracking.objects.filter(program_id=program_pk)
        .prefetch_related("contract")
    )

    # Loop all tracking objects
    for tracking in tracking_numbers:
        month = datetime.strftime(tracking.contract.date_issued, "%Y-%m")

        if month not in monthstats["status"]:
            monthstats["status"][month] = {}    # status of all contracts issued during a given month

        # Gather stats on all contracts' statuses
        if tracking.contract.status not in monthstats["status"][month]:
            monthstats["status"][month][tracking.contract.status] = 0
        monthstats["status"][month][tracking.contract.status] += 1

        # For finished contracts, gather more data
        if tracking.contract.status == "finished":
            if month not in monthstats["n"]:
                monthstats["n"][month] = 0          # Number of finished contracts that month
                monthstats["isk"][month] = 0        # Amount of ISK exchanged that month
                monthstats["items"][month] = {}     # Highest ISK items
                monthstats["users"][month] = {}     # Highest ISK users
            monthstats["isk"][month] += tracking.contract.price
            monthstats["n"][month] += 1

            # Collect ISK data per user
            user = tracking.contract.assignee_id
            if not user in monthstats["users"][month]:
                monthstats["users"][month][user] = 0
            monthstats["users"][month][user] += tracking.contract.price

            # Collect ISK data per items
            tracking_items = TrackingItem.objects.filter(tracking=tracking)
            for item in tracking_items:
                if not item in monthstats["items"][month]:
                    monthstats["items"][month][item] = {"descript": item.eve_type, "isk": 0, "q": 0 }
                monthstats["items"][month][item]["isk"] += item.buy_value
                monthstats["items"][month][item]["q"] += item.quantity


    # Calculate top 10 users and items for each month
    for month in monthstats["items"].keys():
        h_item = []
        h_user = []
        for it in sorted(monthstats["items"][month], key=lambda x: -monthstats["items"][month][x]["isk"]):
            h_item.append((it.eve_type.name, f"https://image.eveonline.com/Type/{it.eve_type.id}_32.png", monthstats["items"][month][it]["isk"]))
            if len(h_item) == 10:
                break

        for u in sorted(monthstats["users"][month], key=lambda x: -monthstats["users"][month][x]):
            user = EveEntity.objects.resolve_name(u)
            h_user.append((user, f"https://images.evetech.net/characters/{u}/portrait?size=32", monthstats["users"][month][u]))
            if len(h_user) == 10:
                break


        monthstats["items"][month] = h_item
        monthstats["users"][month] = h_user

    # Reformat data so that it is easier to use billboard.js
    for cat in ("isk", "n"):
        x = ["x", ]
        y = [cat, ]
        for m in sorted(monthstats[cat].keys()):
            x.append(m)
            if cat == "isk":
                y.append("%.2f" % (monthstats[cat][m] / 1.0e9))
            else:
                y.append(monthstats[cat][m])
        monthstats[cat] = {"x": x, "y": y}

    context = {
        "stats": json.dumps(monthstats),
    }

    return render(request, "buybackprogram/performance.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def program_stats(request):

    # List for valid contracts to be displayed
    valid_contracts = []

    # Tracker values
    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    # Request user owned characters
    characters = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__character_id", flat=True
    )

    # Request user owned corporations
    corporations = CharacterOwnership.objects.filter(user=request.user).values_list(
        "character__corporation_id", flat=True
    )

    # Get all tracking objects that have a linked contract to them for the user
    tracking_numbers = (
        Tracking.objects.filter(contract__isnull=False)
        .filter(
            Q(contract__assignee_id__in=characters)
            | Q(contract__assignee_id__in=corporations)
        )
        .filter(contract__date_expired__gte=timezone.now())
        .prefetch_related("contract")
    )

    # Loop tracking objects to see if we have any contracts
    for tracking in tracking_numbers:

        # Get notes for this contract
        tracking.contract.notes = ContractNotification.objects.filter(
            contract=tracking.contract
        )

        # Walk the tracker values for contracts
        if tracking.contract.status == "outstanding":
            values["outstanding"] += tracking.contract.price
            values["outstanding_count"] += 1
        if tracking.contract.status == "finished":
            values["finished"] += tracking.contract.price
            values["finished_count"] += 1

        # Get the name for the issuer
        tracking.contract.issuer_name = EveEntity.objects.resolve_name(
            tracking.contract.issuer_id
        )

        # Get the name for the assignee
        tracking.contract.assignee_name = EveEntity.objects.resolve_name(
            tracking.contract.assignee_id
        )

        # Add contract to the valid contract list
        valid_contracts.append(tracking)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.see_all_statics")
def program_stats_all(request):

    # List for valid contracts to be displayed
    valid_contracts = []

    # Tracker values
    values = {
        "outstanding": 0,
        "finished": 0,
        "outstanding_count": 0,
        "finished_count": 0,
    }

    # Get all tracking objects that have a linked contract to them for the user
    tracking_numbers = (
        Tracking.objects.filter(contract__isnull=False)
        .filter(contract__date_expired__gte=timezone.now())
        .prefetch_related("contract")
    )

    # Loop tracking objects to see if we have any contracts
    for tracking in tracking_numbers:

        # Get notes for this contract
        tracking.contract.notes = ContractNotification.objects.filter(
            contract=tracking.contract
        )

        # Walk the tracker values for contracts
        if tracking.contract.status == "outstanding":
            values["outstanding"] += tracking.contract.price
            values["outstanding_count"] += 1
        if tracking.contract.status == "finished":
            values["finished"] += tracking.contract.price
            values["finished_count"] += 1

        # Get the name for the issuer
        tracking.contract.issuer_name = EveEntity.objects.resolve_name(
            tracking.contract.issuer_id
        )

        # Get the name for the assignee
        tracking.contract.assignee_name = EveEntity.objects.resolve_name(
            tracking.contract.assignee_id
        )

        valid_contracts.append(tracking)

    context = {
        "contracts": valid_contracts,
        "values": values,
        "mine": True,
    }

    return render(request, "buybackprogram/stats.html", context)


@login_required
@permission_required("buybackprogram.basic_access")
def contract_details(request, contract_title):

    contract = Contract.objects.get(title__contains=contract_title)

    # Get notes for this contract
    notes = ContractNotification.objects.filter(contract=contract)

    # Get items for this contract
    contract_items = ContractItem.objects.filter(contract=contract)

    # Get tracking object for this contract
    tracking = Tracking.objects.get(
        tracking_number=contract_title,
    )

    # Get tracked items
    tracking_items = TrackingItem.objects.filter(tracking=tracking)

    # Find the difference in the created contract and original calculation
    for tracking_item in tracking_items:

        tracking_notes = []

        item_match = False
        quantity_match = False

        for contract_item in contract_items:
            if contract_item.eve_type == tracking_item.eve_type:
                item_match = True

                if contract_item.quantity == tracking_item.quantity:
                    quantity_match = True
                    break

        tracking_item.item_match = item_match

        if not item_match:
            tracking_notes.append(note_missing_from_contract(tracking_item.eve_type))

        if item_match and not quantity_match:
            tracking_notes.append(
                note_quantity_missing_from_contract(tracking_item.eve_type)
            )

        tracking_item.notes = tracking_notes

    for contract_item in contract_items:

        contract_notes = []

        item_match = False
        quantity_match = False

        for tracking_item in tracking_items:
            if contract_item.eve_type == tracking_item.eve_type:
                item_match = True

                if contract_item.quantity == tracking_item.quantity:
                    quantity_match = True
                    break

        contract_item.item_match = item_match

        if not item_match:
            contract_notes.append(note_missing_from_tracking(contract_item.eve_type))

        if item_match and not quantity_match:
            contract_notes.append(
                note_quantity_missing_from_tracking(contract_item.eve_type)
            )

        contract_item.notes = contract_notes

    # Get the name for the issuer
    contract.issuer_name = EveEntity.objects.resolve_name(contract.issuer_id)

    # Get the name for the assignee
    contract.assignee_name = EveEntity.objects.resolve_name(contract.assignee_id)

    context = {
        "notes": notes,
        "contract": contract,
        "contract_items": contract_items,
        "tracking": tracking,
        "tracking_items": tracking_items,
    }

    return render(request, "buybackprogram/contract_details.html", context)
