"""Delete contract duplicates."""

from django.db import migrations
from collections import Counter


def forwards(apps, schema_editor):
    Contract = apps.get_model("buybackprogram", "Contract")
    duplicate_ids = _identify_duplicates(Contract)
    if not duplicate_ids:
        print("No duplicate contracts to delete.", end="")
        return
    duplicate_contracts = Contract.objects.filter(
        contract_id__in=duplicate_ids, no_tracking=False
    )
    duplicate_contracts.filter(tracking__isnull=True).delete()
    print(f"Deleted {len(duplicate_ids)} duplicate contracts.", end="")
    if remaining_duplicates := _identify_duplicates(Contract):
        print(
            f" ERROR: {len(remaining_duplicates)} duplicate contracts remaining. "
            "Can not proceed."
        )
        exit(1)


def _identify_duplicates(Contract) -> set:
    ids = list(Contract.objects.values_list("contract_id", flat=True))
    ids_counted = Counter(ids)
    return {id for id, count in ids_counted.items() if count > 1}


class Migration(migrations.Migration):
    dependencies = [
        ("buybackprogram", "0010_contract_no_tracking_alter_tracking_tracking_number"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
