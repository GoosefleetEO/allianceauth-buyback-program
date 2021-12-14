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

from buybackprogram.forms import ProgramForm, ProgramItemForm
from buybackprogram.models import Owner, Program, ProgramItem
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
    form = ProgramForm(request.POST or None, user=request.user)

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

    instance = Program.objects.get(pk=program_pk)

    if request.method == "POST":
        form = ProgramForm(request.POST)

        logger.debug(
            "Received POST request containing update program form, is valid: %s"
            % form.is_valid()
        )

        if form.is_valid():

            form = ProgramForm(request.POST, instance=instance)

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

            ProgramItem.objects.update_or_create(
                item_type=item_type,
                program=program,
                defaults={
                    "item_tax": item_tax,
                    "disallow_item": disallow_item,
                },
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
def program_item_remove(request, item_pk):

    program_item = ProgramItem.objects.get(item_type=item_pk)

    program_item.delete()

    messages_plus.warning(
        request,
        format_html(gettext_lazy("Deleted item from program")),
    )

    return redirect("buybackprogram:index")
