from django.core.management.base import BaseCommand
from eveuniverse.models import EveSolarSystem, EveType


def get_input(text):
    """wrapped input to enable unit testing / patching"""
    return input(text)


class Command(BaseCommand):
    help = "Setup all needed data for buyback program to operate"

    def _update_models(self):
        """updates all SDE models from ESI and provides progress output"""
        models = [
            EveSolarSystem,
            EveType,
        ]
        model_count = 0
        for EveModel in models:
            model_count += 1
            self.stdout.write(
                "Updating objects for %s (%d/%d)..."
                % (EveModel.__name__, model_count, len(models))
            )
            EveModel.objects.update_or_create_all_esi(
                include_children=True, wait_for_children=False
            )

    def handle(self, *args, **options):
        self.stdout.write(
            "This command will load all the required data needed for the program to operate."
            "This process will take a very long time as we are loading every single items and solar system from ESI."
        )
        user_input = get_input("Are you sure you want to proceed? (y/N)?")
        if user_input.lower() == "y":
            self._update_models()
            self.stdout.write(
                "Fetch tasks added to worker queue. You can monitor the progress of these tasks from your dashboard."
            )
        else:
            self.stdout.write("Aborted")
