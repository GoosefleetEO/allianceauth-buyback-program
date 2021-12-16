from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy
from esi.decorators import token_required

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.forms import LocationForm, ProgramForm, ProgramItemForm
from buybackprogram.models import Location, Owner, Program, ProgramItem
from buybackprogram.utils import messages_plus

logger = get_extension_logger(__name__)


@login_required
@permission_required("buybackprogram.manage_programs")
@token_required(
    scopes=[
        "esi-contracts.read_character_contracts.v1",
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
    form = ProgramForm(request.POST or None, user=request.user)

    if request.POST and form.is_valid():

        form = ProgramForm(request.POST, user=request.user)

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


@login_required
@permission_required("buybackprogram.manage_programs")
def program_edit(request, program_pk):

    instance = Program.objects.get(pk=program_pk)

    if request.method == "POST":
        form = ProgramForm(request.POST, user=request.user)

        logger.debug(
            "Received POST request containing update program form, is valid: %s"
            % form.is_valid()
        )

        if form.is_valid():

            form = ProgramForm(request.POST, instance=instance, user=request.user)

            updated_program = form.save()

            messages_plus.success(
                request,
                format_html(
                    gettext_lazy("Program updated at %(location)s")
                    % {
                        "location": format_html(
                            "<strong>{}</strong>", updated_program.location
                        ),
                    }
                ),
            )

            return HttpResponseRedirect(reverse("buybackprogram:index"))

    else:

        form = ProgramForm(instance=instance, user=request.user)

    context = {
        "program": instance,
        "form": form,
    }

    return render(request, "buybackprogram/program_edit.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def location_add(request):

    locations = Location.objects.all()

    if request.method != "POST":
        form = LocationForm()
    else:
        form = LocationForm(
            request.POST,
            value=int(request.POST["eve_solar_system"]),
        )

        if form.is_valid():
            eve_solar_system = form.cleaned_data["eve_solar_system"]
            name = form.cleaned_data["name"]

            created = Location.objects.update_or_create(
                eve_solar_system=eve_solar_system,
                name=name,
                defaults={
                    "eve_solar_system": eve_solar_system,
                    "name": name,
                },
            )

            if created:
                messages_plus.success(
                    request,
                    format_html(
                        "Added location for <strong>{}</strong> in system <strong>{}</strong>",
                        name,
                        eve_solar_system,
                    ),
                )

            return HttpResponseRedirect(request.path_info)

    context = {
        "locations": locations,
        "form": form,
    }

    return render(request, "buybackprogram/location_add.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def program_edit_item(request, program_pk):
    program = Program.objects.get(pk=program_pk)

    program_items = ProgramItem.objects.filter(program=program)

    if request.method != "POST":
        form = ProgramItemForm()
    else:
        form = ProgramItemForm(
            request.POST,
            value=int(request.POST["item_type"]),
        )

        if form.is_valid():
            item_type = form.cleaned_data["item_type"]
            item_tax = form.cleaned_data["item_tax"]
            disallow_item = form.cleaned_data["disallow_item"]

            created = ProgramItem.objects.update_or_create(
                item_type=item_type,
                program=program,
                defaults={
                    "item_tax": item_tax,
                    "disallow_item": disallow_item,
                },
            )

            if created:
                messages_plus.success(
                    request,
                    format_html(
                        "Added <strong>{}</strong> to program with <strong>{}</strong> % tax",
                        item_type,
                        item_tax,
                    ),
                )

            return HttpResponseRedirect(request.path_info)

    context = {
        "program": program,
        "program_items": program_items,
        "form": form,
    }

    return render(request, "buybackprogram/program_edit_item.html", context)


@login_required
@permission_required("buybackprogram.manage_programs")
def program_remove(request, program_pk):

    program = Program.objects.get(pk=program_pk)

    if program.owner.user == request.user:
        program.delete()

        messages_plus.warning(
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


@login_required
@permission_required("buybackprogram.manage_programs")
def program_item_remove(request, item_pk, program_pk):

    program_item = ProgramItem.objects.get(item_type=item_pk)

    name = program_item.item_type

    program_item.delete()

    messages_plus.warning(
        request,
        format_html(
            "Deleted <strong>{}</strong> from program",
            name,
        ),
    )

    return redirect("buybackprogram:program_edit_item", program_pk)
