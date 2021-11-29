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
from buybackprogram.helpers import get_price, get_refined_price
from buybackprogram.models import ItemPrices, Owner, Program, ProgramItem
from buybackprogram.utils import messages_plus

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.basic_access")
def index(request):
    context = {"programs": Program.objects.filter()}

    return render(request, "buybackprogram/index.html", context)


@login_required
@permission_required("buybackprogram.setup_retriever")
@token_required(
    scopes=[
        "esi-universe.read_structures.v1",
        "esi-assets.read_corporation_assets.v1",
        "esi-contracts.read_corporation_contracts.v1",
    ]
)
def setup(request, token):
    success = True
    token_char = EveCharacter.objects.get(character_id=token.character_id)

    try:
        owned_char = CharacterOwnership.objects.get(
            user=request.user, character=token_char
        )
    except CharacterOwnership.DoesNotExist:
        messages_plus.error(
            request,
            format_html(
                gettext_lazy(
                    "You can only use your main or alt characters "
                    "to add corporations. "
                    "However, character %s is neither. "
                )
                % format_html("<strong>{}</strong>", token_char.character_name)
            ),
        )
        success = False

    if success:
        try:
            corporation = EveCorporationInfo.objects.get(
                corporation_id=token_char.corporation_id
            )
        except EveCorporationInfo.DoesNotExist:
            corporation = EveCorporationInfo.objects.create_corporation(
                token_char.corporation_id
            )

        with transaction.atomic():
            owner, _ = Owner.objects.update_or_create(
                corporation=corporation, character=owned_char
            )

            owner.save()

        messages_plus.info(
            request,
            format_html(
                gettext_lazy(
                    "%(corporation)s has been added with %(character)s "
                    "as program manager. "
                )
                % {
                    "corporation": format_html(
                        "<strong>{}</strong>", owner.corporation
                    ),
                    "character": format_html(
                        "<strong>{}</strong>", owner.character.character.character_name
                    ),
                }
            ),
        )

    return redirect("buybackprogram:index")


@login_required
@permission_required("buybackprogram.manage_programs")
def program_add(request):
    context = {"action": "Create Program"}

    # create object of form
    form = ProgramForm(request.POST or None)

    # check if form data is valid
    if request.POST and form.is_valid():
        # save the form data to model
        form.save()

        return HttpResponseRedirect(reverse("buybackprogram:index"))

    context["form"] = form

    return render(request, "buybackprogram/program_add.html", context)


def program_edit(request, program_pk):
    program = Program.objects.filter(pk=program_pk).first()

    if program is None:
        return redirect("buybackprogram:index")

    # create object of form
    form = ProgramForm(request.POST or None)

    # check if form data is valid
    if request.POST and form.is_valid():
        # save the form data to model
        form.save()

        return HttpResponseRedirect(reverse("buybackprogram:index"))

    context = {
        "program": program,
        "form": form,
    }

    return render(request, "buybackprogram/program_edit.html", context)


def program_edit_item(request, program_pk):
    program = Program.objects.filter(pk=program_pk).first()

    if program is None:
        return redirect("buybackprogram:index")

    # create object of form
    form = ProgramItemForm(request.POST or None)

    # check if form data is valid
    if request.POST and form.is_valid():
        # save the form data to model
        form.save()

        return HttpResponseRedirect(reverse("buybackprogram:index"))

    context = {
        "program": program,
        "form": form,
    }

    return render(request, "buybackprogram/program_edit_item.html", context)


@login_required
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
