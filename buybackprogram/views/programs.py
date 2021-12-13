from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy
from esi.decorators import token_required

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.forms import ProgramForm, ProgramItemForm
from buybackprogram.models import Owner, Program
from buybackprogram.utils import messages_plus

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.setup_retriever")
@token_required(
    scopes=[
        "esi-contracts.read_character_contracts.v1",
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
                corporation=corporation, character=owned_char, user=request.user
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
    form = ProgramForm(request.POST or None)

    if request.POST and form.is_valid():

        form = ProgramForm(request.POST)

        new_program = form.save()

        messages_plus.success(
            request,
            format_html(
                gettext_lazy("New program created at %(location)s")
                % {
                    "location": format_html(
                        "<strong>{}</strong>", new_program.location
                    ),
                }
            ),
        )

        return HttpResponseRedirect(reverse("buybackprogram:index"))

    return render(request, "buybackprogram/program_add.html", {"form": form})


def program_edit(request, program_pk):

    program = get_object_or_404(Program, pk=program_pk)

    if request.method == "POST":
        form = ProgramForm(request.POST)

        logger.debug(
            "Received POST request containing update program form, is valid: %s"
            % form.is_valid()
        )

        if form.is_valid():

            program.owner = Owner.objects.get(user=request.user)
            program.is_corporation = form.cleaned_data["is_corporation"]
            program.location = form.cleaned_data["location"]
            program.tax = form.cleaned_data["tax"]
            program.hauling_fuel_cost = form.cleaned_data["hauling_fuel_cost"]
            program.price_dencity_modifier = form.cleaned_data["price_dencity_modifier"]
            program.price_dencity_treshold = form.cleaned_data["price_dencity_treshold"]
            program.price_dencity_tax = form.cleaned_data["price_dencity_tax"]
            program.allow_all_items = form.cleaned_data["allow_all_items"]
            program.use_refined_value = form.cleaned_data["use_refined_value"]
            program.use_compressed_value = form.cleaned_data["use_compressed_value"]
            program.use_raw_ore_value = form.cleaned_data["use_raw_ore_value"]
            program.allow_unpacked_items = form.cleaned_data["allow_unpacked_items"]
            program.refining_rate = form.cleaned_data["refining_rate"]
            program.restricted_to_group = form.cleaned_data["restricted_to_group"]
            program.restricted_to_state = form.cleaned_data["restricted_to_state"]

            program.save()

            return HttpResponseRedirect(reverse("buybackprogram:index"))

    else:

        data = {
            "is_corporation": program.is_corporation,
            "location": program.location,
            "tax": program.tax,
            "hauling_fuel_cost": program.hauling_fuel_cost,
            "price_dencity_modifier": program.price_dencity_modifier,
            "price_dencity_treshold": program.price_dencity_treshold,
            "price_dencity_tax": program.price_dencity_tax,
            "allow_all_items": program.allow_all_items,
            "use_refined_value": program.use_refined_value,
            "use_compressed_value": program.use_compressed_value,
            "use_raw_ore_value": program.use_raw_ore_value,
            "allow_unpacked_items": program.allow_unpacked_items,
            "refining_rate": program.refining_rate,
            "restricted_to_group": program.restricted_to_group,
            "restricted_to_state": program.restricted_to_state,
        }

        form = ProgramForm(initial=data)

    context = {
        "program": program,
        "form": form,
    }

    return render(request, "buybackprogram/program_edit.html", context)


def program_edit_item(request, program_pk):
    program = Program.objects.get(pk=program_pk)

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
@permission_required("buybackprogram.manage_programs")
def program_remove(request, program_pk):

    program = Program.objects.get(pk=program_pk)

    if program.owner.user == request.user:
        program.delete()

        messages_plus.danger(
            request,
            format_html(
                gettext_lazy("Deleted program for %(location)s")
                % {
                    "location": format_html("<strong>{}</strong>", program.location),
                }
            ),
        )

    else:
        messages_plus.error(
            request,
            format_html(
                gettext_lazy(
                    "You do not own this program and thus you can't delete it."
                )
            ),
        )

    return redirect("buybackprogram:index")
