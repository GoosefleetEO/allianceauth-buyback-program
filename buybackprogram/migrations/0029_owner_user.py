# Generated by Django 3.2.8 on 2021-12-13 17:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("buybackprogram", "0028_tracking_tracking_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="owner",
            name="user",
            field=models.ForeignKey(
                default=1,
                help_text="User that manages the program",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="auth.user",
            ),
            preserve_default=False,
        ),
    ]