from django.core.management.base import BaseCommand
from eveuniverse.models import EveMarketGroup


class Command(BaseCommand):
    help = "Preloads data required for the buyback program from ESI"

    def handle(self, *args, **options):
        EveMarketGroup.objects.update_or_create_all_esi(
            include_children=True, wait_for_children=False
        )
