from django.core.management.base import BaseCommand
from eveuniverse.models import EveSolarSystem, EveType


class Command(BaseCommand):
    help = "Preloads data required for the buyback program from ESI"

    def handle(self, *args, **options):
        EveType.objects.update_or_create_all_esi(
            include_children=False, wait_for_children=False
        )

        EveSolarSystem.objects.update_or_create_all_esi(
            include_children=False, wait_for_children=False
        )
