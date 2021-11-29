from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy
from esi.decorators import token_required
from eveuniverse.models import EveType

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.constants import REFINING_EVE_CATEGORIES
from buybackprogram.forms import CalculatorForm, ProgramForm, ProgramItemForm
from buybackprogram.helpers import get_item_prices, get_price, get_refined_price
from buybackprogram.models import ItemPrices, Owner, Program, ProgramItem
from buybackprogram.utils import messages_plus

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybacks.basic_access")
def program_calculate(request, program_pk):

    program = Program.objects.filter(pk=program_pk).first()

    buyback_data = []

    if program is None:
        return redirect("buybackprogram:index")

    if request.method != "POST":

        form = CalculatorForm(program=program)

    else:
        form = CalculatorForm(request.POST, program=program)

        if form.is_valid():
            form_items = form.cleaned_data["items"]

            # If we have an ingame copy paste
            if "\t" in form_items:
                # Split items by rows
                for item in form_items.split("\n"):
                    # get item name and quantity
                    parts = item.split("\t")
                    # If we have an quantity row
                    if len(parts) >= 2:
                        # Get item name from the first part
                        name = parts[0]

                        # Get quantities and format the different localization imputs
                        quantity = int(
                            parts[1]
                            .replace(" ", "")
                            .replace(".", "")
                            .replace("\xa0", "")
                        )

                        # Get type data for the item

                        item_type = EveType.objects.filter(name=name).first()

                        if item_type:

                            # Get any special item taxes or limitations we might have added
                            program_item_settings = ProgramItem.objects.filter(
                                program=program, item_type__id=item_type.id
                            ).first()

                            # Get all item price datas
                            item_prices = get_item_prices(
                                item_type,
                                name,
                                quantity,
                                program,
                                program_item_settings,
                            )

                            # Final form of the built buyback item that will be pushed to the item array
                            buyback_item = {
                                "type_data": item_type,
                                "item_prices": item_prices,
                            }

                            # Append buyback item data to the total array
                            buyback_data.append(buyback_item)

                        else:
                            logger.debug(
                                "TODO: Error handling when item has no typedata (new or missing items)"
                            )

                    else:
                        logger.debug(
                            "TODO: process items when there are items without quantities"
                        )

            else:
                logger.debug("TODO: add tasks to process plain text imputs here.")

    context = {
        "program": program,
        "form": form,
        "buyback_data": buyback_data,
        "total": "TODO: total",
    }

    return render(request, "buybackprogram/program_calculate.html", context)


"""@login_required
@permission_required("buybacks.basic_access")
def program_calculate(request, program_pk):
    program = Program.objects.filter(pk=program_pk).first()
    data = []
    total = 0

    if program is None:
        return redirect("buybackprogram:index")

    if request.method != "POST":
        form = CalculatorForm(program=program)
    else:
        form = CalculatorForm(request.POST, program=program)

        if form.is_valid():
            items = form.cleaned_data["items"]

            # For copy pasted items
            if "\t" in items:

                # Split items by rows
                for item in items.split("\n"):

                    parts = item.split("\t")

                    # Get item name and quanity
                    if len(parts) >= 2:
                        name = parts[0]

                        quantity = int(
                            parts[1]
                            .replace(" ", "")
                            .replace(".", "")
                            .replace("\xa0", "")
                        )

                        # Get evetype data for the item
                        item_data = EveType.objects.filter(name=name).first()

                        # TODO: If no data found

                        # Get special taxations
                        item_tax = ProgramItem.objects.filter(
                            program=program, item_type__name=name
                        ).first()

                        # Get item price
                        item_price = ItemPrices.objects.filter(id=item_data.id).first()

                        # If special taxation
                        if item_tax:
                            disallowed_item = item_tax.disallow_item

                            # If refined price is used
                            if (
                                item_data.eve_group.eve_category.id
                                in REFINING_EVE_CATEGORIES
                                and program.use_refined_value
                            ):

                                materials = get_refined_price(
                                    item_data.id,
                                    program.tax + item_tax.item_tax,
                                    program.refining_rate,
                                    disallowed_item,
                                )

                            # No refined price is used aka. raw price
                            else:
                                materials = False

                            price_data = get_price(
                                program.tax + item_tax.item_tax,
                                quantity,
                                item_price,
                                disallowed_item,
                            )

                        # If item has no special taxes
                        else:
                            disallowed_item = False

                            # If refiend price is used
                            if (
                                item_data.eve_group.eve_category.id
                                in REFINING_EVE_CATEGORIES
                                and program.use_refined_value
                            ):

                                materials = get_refined_price(
                                    item_data.id,
                                    program.tax,
                                    program.refining_rate,
                                    disallowed_item,
                                )

                            # If refined price is not used aka. raw price
                            else:
                                materials = False

                            price_data = get_price(
                                program.tax, quantity, item_price, disallowed_item
                            )

                        buyback_item = {
                            "name": name,
                            "quantity": quantity,
                            "material": materials,
                            "type_id": item_data.id,
                            "type": price_data,
                        }

                        data.append(buyback_item)

    context = {
        "program": program,
        "form": form,
        "data": data,
        "total": total,
    }

    return render(request, "buybackprogram/program_calculate.html", context)
"""
