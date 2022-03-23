# Generated by Django 3.2.10 on 2022-03-23 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buybackprogram", "0003_statics_performance_increase"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="program",
            name="location",
        ),
        migrations.AddField(
            model_name="program",
            name="location",
            field=models.ManyToManyField(
                help_text="The location where contracts should be created at.",
                related_name="_buybackprogram_program_location_+",
                to="buybackprogram.Location",
            ),
        ),
    ]
