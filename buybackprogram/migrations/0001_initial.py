# Generated by Django 3.2.10 on 2022-01-08 14:35

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import buybackprogram.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("eveuniverse", "0005_type_materials_and_sections"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("eveonline", "0015_factions"),
        ("authentication", "0019_merge_20211026_0919"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="General",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("basic_access", "Can access this app and see own statics."),
                    (
                        "manage_programs",
                        "Can manage own buyback programs and see own program statics.",
                    ),
                    ("see_all_statics", "Can see all program statics."),
                ),
                "managed": False,
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Contract",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("assignee_id", models.IntegerField()),
                ("availability", models.CharField(max_length=20)),
                ("contract_id", models.IntegerField()),
                ("date_completed", models.DateTimeField(null=True)),
                ("date_expired", models.DateTimeField(null=True)),
                ("date_issued", models.DateTimeField()),
                ("for_corporation", models.BooleanField()),
                ("issuer_corporation_id", models.IntegerField()),
                ("issuer_id", models.IntegerField()),
                ("start_location_id", models.BigIntegerField(null=True)),
                ("price", models.BigIntegerField()),
                ("status", models.CharField(max_length=30)),
                ("title", models.CharField(max_length=128)),
                ("volume", models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Structure name where the contracts are accepted at",
                        max_length=32,
                    ),
                ),
                (
                    "structure_id",
                    models.BigIntegerField(
                        blank=True,
                        default=None,
                        help_text="The ID for the structure you wish to accept the contracts at. If left empty the program statistics page will not track if the contract is actually made at the correct structure or not. To get the ID for the structure see readme for getting structure IDs",
                        null=True,
                        verbose_name="Ingame unique ID for structure",
                    ),
                ),
                (
                    "eve_solar_system",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        help_text="System where the buyback structure is located",
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        related_name="+",
                        to="eveuniverse.evesolarsystem",
                        verbose_name="Solar system",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Owner",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "character",
                    models.ForeignKey(
                        help_text="Character used for retrieving info",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="authentication.characterownership",
                    ),
                ),
                (
                    "corporation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="eveonline.evecorporationinfo",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User that manages the program",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Program",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_corporation",
                    models.BooleanField(
                        default=False,
                        help_text="If we should use the corporation of the manager as the contract receiver instead of the character.",
                    ),
                ),
                (
                    "tax",
                    models.IntegerField(
                        default=0,
                        help_text="A default tax rate in this program that is applied on all items.",
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="Default tax",
                    ),
                ),
                (
                    "hauling_fuel_cost",
                    models.IntegerField(
                        default=0,
                        help_text="ISK per m³ that will be removed from the buy price ie. to cover jump freighet fuel costs. <b>Should not be used with price dencity modifier</b>",
                        verbose_name="Hauling fuel cost per m³",
                    ),
                ),
                (
                    "price_dencity_modifier",
                    models.BooleanField(
                        default=False,
                        help_text="Should we modify buy prices for items with high volume and low value ie. T1 industrial hulls. <b>Should not be used with hauling fuel cost</b>",
                        verbose_name="Price density modifier",
                    ),
                ),
                (
                    "price_dencity_treshold",
                    models.IntegerField(
                        default=0,
                        help_text="At what ISK/m3 do we start to apply the low isk dencity tax. Tritanium is 500 ISK/m³ @ 5 ISK per unit price. PLEX is 14,5Trillion ISK/m³ @2.9M per unit price.",
                        null=True,
                        verbose_name="Price density threshold",
                    ),
                ),
                (
                    "price_dencity_tax",
                    models.IntegerField(
                        default=0,
                        help_text="How much tax do we apply on the low isk density items.",
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="Price density tax",
                    ),
                ),
                (
                    "allow_all_items",
                    models.BooleanField(
                        default=True,
                        help_text="If true all items are accepted to the buyback program. You can set extra taxes or disallow individual items from the program item section. If set to false you need to add each accepted item into the program item section. Blueprints are not included in all items.",
                    ),
                ),
                (
                    "use_refined_value",
                    models.BooleanField(
                        default=False,
                        help_text="Take refined value into account when calculating prices for ore, ice and moon goo",
                        verbose_name="Ore: Use refined value",
                    ),
                ),
                (
                    "use_compressed_value",
                    models.BooleanField(
                        default=False,
                        help_text="Take compressed value into account when calculating prices for ore, ice and moon goo",
                        verbose_name="Ore: Use compressed value",
                    ),
                ),
                (
                    "use_raw_ore_value",
                    models.BooleanField(
                        default=True,
                        help_text="Take raw ore value into account when calculating prices for ore, ice and moon goo",
                        verbose_name="Ore: Use raw value",
                    ),
                ),
                (
                    "allow_unpacked_items",
                    models.BooleanField(
                        default=False,
                        help_text="Do you want to allow unpacked items in this program such as assembled ship hulls?",
                        verbose_name="Allow unpacked items",
                    ),
                ),
                (
                    "refining_rate",
                    models.IntegerField(
                        default=0,
                        help_text="Refining rate to be used if ore refined value is active",
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                        verbose_name="Refining rate",
                    ),
                ),
                (
                    "blue_loot_npc_price",
                    models.BooleanField(
                        default=False,
                        help_text="Use NPC price as value for blue loot",
                        verbose_name="NPC price for: Sleeper Components",
                    ),
                ),
                (
                    "red_loot_npc_price",
                    models.BooleanField(
                        default=False,
                        help_text="Use NPC price as value for red loot",
                        verbose_name="NPC price for: Triglavian Survey Database",
                    ),
                ),
                (
                    "ope_npc_price",
                    models.BooleanField(
                        default=False,
                        help_text="Use NPC price as value for OPEs",
                        verbose_name="NPC price for: Overseer's Personal Effects",
                    ),
                ),
                (
                    "discord_dm_notification",
                    models.BooleanField(
                        default=False,
                        help_text="Check if you want to receive a direct message notification each time a new contract is created. <b>Requires aa-discordbot app or discordproxy app to work</b>",
                        verbose_name="Discord direct messages for new contracts",
                    ),
                ),
                (
                    "discord_channel_notification",
                    models.BigIntegerField(
                        blank=True,
                        help_text="Check if you want to feed new contracts to a discord channel. <b>Requires aa-discordbot app or discordproxy app to work</b>",
                        null=True,
                        verbose_name="Discord channel ID for notifications",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        help_text="The location where contracts should be created at.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="buybackprogram.location",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        help_text="Character that is used to manage this program.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="buybackprogram.owner",
                        verbose_name="Manager",
                    ),
                ),
                (
                    "restricted_to_group",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The group(s) that will be able to see this buyback program. If none is selected program is open for all.",
                        related_name="buybackprogram_require_groups",
                        to="auth.Group",
                    ),
                ),
                (
                    "restricted_to_state",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The state(s) that will be able to see this buyback program. If none is selected program is open for all.",
                        related_name="buybackprogram_require_states",
                        to="authentication.State",
                    ),
                ),
            ],
            options={
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Tracking",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.BigIntegerField()),
                ("taxes", models.BigIntegerField()),
                ("hauling_cost", models.BigIntegerField()),
                ("donation", models.BigIntegerField(blank=True, null=True)),
                ("net_price", models.BigIntegerField()),
                ("tracking_number", models.CharField(max_length=20)),
                (
                    "issuer_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="buybackprogram.program",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("disable_notifications", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=models.SET(buybackprogram.models.get_sentinel_user),
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Settings",
                "verbose_name_plural": "User Settings",
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="TrackingItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("buy_value", models.BigIntegerField()),
                ("quantity", models.IntegerField()),
                (
                    "eve_type",
                    models.ForeignKey(
                        help_text="Item type information",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eveuniverse.evetype",
                    ),
                ),
                (
                    "tracking",
                    models.ForeignKey(
                        help_text="What tracking do these items belong to",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="buybackprogram.tracking",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="location",
            name="owner",
            field=models.ForeignKey(
                help_text="Player managing this location",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="buybackprogram.owner",
                verbose_name="Manager",
            ),
        ),
        migrations.CreateModel(
            name="ItemPrices",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("buy", models.BigIntegerField()),
                ("sell", models.BigIntegerField()),
                ("updated", models.DateTimeField()),
                (
                    "eve_type",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eveuniverse.evetype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ContractItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField()),
                (
                    "contract",
                    models.ForeignKey(
                        help_text="What contract do these items belong to",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="buybackprogram.contract",
                    ),
                ),
                (
                    "eve_type",
                    models.ForeignKey(
                        help_text="Item type information",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eveuniverse.evetype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProgramItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "item_tax",
                    models.IntegerField(
                        default=0,
                        help_text="How much do you want to adjust the default tax on this item. Can be a positive or a negative value.",
                        null=True,
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(-100),
                        ],
                        verbose_name="Item tax adjustment",
                    ),
                ),
                (
                    "disallow_item",
                    models.BooleanField(
                        default=False,
                        help_text="You can disallow an item from a buyback location. It will return 0 price if disallowed.",
                        verbose_name="Disallow item in program",
                    ),
                ),
                (
                    "item_type",
                    models.ForeignKey(
                        help_text="Select item for special tax",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eveuniverse.evetype",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        help_text="What program do these items belong to",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="buybackprogram.program",
                    ),
                ),
            ],
            options={
                "default_permissions": (),
                "unique_together": {("program", "item_type")},
            },
        ),
    ]
