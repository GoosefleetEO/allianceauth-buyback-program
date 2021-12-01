# Generated by Django 3.2.8 on 2021-11-26 20:36

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eveuniverse", "0005_type_materials_and_sections"),
        ("buybackprogram", "0010_auto_20211126_2033"),
    ]

    operations = [
        migrations.AddField(
            model_name="programitem",
            name="disallow_item",
            field=models.BooleanField(
                default=False,
                help_text="You can disallow an item from a buyback location. It will return 0 price if disallowed.",
            ),
        ),
        migrations.AlterField(
            model_name="programitem",
            name="item_tax",
            field=models.IntegerField(
                default=0,
                help_text="How much tax do we add on top of the base tax for this item. Can also be negative.",
                null=True,
                validators=[
                    django.core.validators.MaxValueValidator(100),
                    django.core.validators.MinValueValidator(1),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="programitem",
            name="item_type",
            field=models.ForeignKey(
                help_text="Select item for special tax",
                on_delete=django.db.models.deletion.CASCADE,
                to="eveuniverse.evetype",
            ),
        ),
        migrations.AlterField(
            model_name="programitem",
            name="program",
            field=models.ForeignKey(
                help_text="What program do these items belong to",
                on_delete=django.db.models.deletion.CASCADE,
                to="buybackprogram.program",
            ),
        ),
    ]