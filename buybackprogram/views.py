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

from buybackprogram.forms import CalculatorForm, ProgramForm, ProgramItemForm
from buybackprogram.helpers import evemarketer
from buybackprogram.models import Location, Owner, Program, ProgramItem
from buybackprogram.utils import messages_plus


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

            program_location = Location.objects.filter(
                name=program,
            ).first()

            print(program_location)

            tax = program.tax

            print(tax)

            if "\t" in items:

                for item in items.split("\n"):

                    parts = item.split("\t")

                    if len(parts) >= 2:
                        name = parts[0]

                        quantity = int(
                            parts[1]
                            .replace(" ", "")
                            .replace(".", "")
                            .replace("\xa0", "")
                        )

                        item_data = EveType.objects.filter(name=name).first()

                        # TODO: If no data found

                        item_tax = ProgramItem.objects.filter(
                            program=program, item_type__name=name
                        )

                        print(item_tax)

                        # TODO: Price store task to store them in database

                        market_data = evemarketer(item_data.id)

                        # TODO: Tax calculations
                        # TODO: Refining calculations
                        # TODO: Allowed items check

                        buyback_item = {
                            "name": name,
                            "quantity": quantity,
                            "type_id": item_data.id,
                            "market_data": market_data[item_data.id],
                        }

                        total += buyback_item["market_data"]["buy"]

                        data.append(buyback_item)

            print(data)
            print(total)

    context = {
        "program": program,
        "form": form,
        "data": data,
        "total": total,
    }

    return render(request, "buybackprogram/program_calculate.html", context)
