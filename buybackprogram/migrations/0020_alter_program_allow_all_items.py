# Generated by Django 3.2.9 on 2021-11-30 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buybackprogram", "0019_auto_20211130_0650"),
    ]

    operations = [
        migrations.AlterField(
            model_name="program",
            name="allow_all_items",
            field=models.BooleanField(
                default=True,
                help_text="If true all items are accepted to the buyback program. You can set extra taxes or disallow individual items from the program item section. If set to false you need to add each accepted item into the program item section. Blueprints are not included in all items.",
            ),
        ),
    ]