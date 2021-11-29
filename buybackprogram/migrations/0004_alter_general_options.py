# Generated by Django 3.2.8 on 2021-11-13 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("buybackprogram", "0003_program_allow_all_items"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="general",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": (
                    ("basic_access", "Can access this app"),
                    ("setup_owner", "Can setup program owner"),
                    ("manage_programs", "Can manage buyback programs"),
                ),
            },
        ),
    ]
