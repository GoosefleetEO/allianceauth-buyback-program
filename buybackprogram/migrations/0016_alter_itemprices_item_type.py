# Generated by Django 3.2.9 on 2021-11-30 06:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eveuniverse", "0005_type_materials_and_sections"),
        ("buybackprogram", "0015_itemprices_item_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="itemprices",
            name="item_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="eveuniverse.evetype",
                unique=True,
            ),
        ),
    ]