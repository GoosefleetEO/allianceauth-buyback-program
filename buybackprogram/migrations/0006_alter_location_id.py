# Generated by Django 3.2.8 on 2021-11-13 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("buybackprogram", "0005_auto_20211113_1117"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
