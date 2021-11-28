from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from eveuniverse.models import EveSolarSystem, EveType

from allianceauth.authentication.models import CharacterOwnership

# Create your models here.
from allianceauth.eveonline.models import EveCorporationInfo


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("setup_owner", "Can setup program owner"),
            ("manage_programs", "Can manage buyback programs"),
        )


class Owner(models.Model):
    """A corporation that has buyback programs"""

    ERROR_NONE = 0
    ERROR_TOKEN_INVALID = 1
    ERROR_TOKEN_EXPIRED = 2
    ERROR_ESI_UNAVAILABLE = 5

    ERRORS_LIST = [
        (ERROR_NONE, "No error"),
        (ERROR_TOKEN_INVALID, "Invalid token"),
        (ERROR_TOKEN_EXPIRED, "Expired token"),
        (ERROR_ESI_UNAVAILABLE, "ESI API is currently unavailable"),
    ]

    corporation = models.OneToOneField(
        EveCorporationInfo,
        primary_key=True,
        on_delete=models.deletion.CASCADE,
        related_name="+",
    )
    character = models.ForeignKey(
        CharacterOwnership,
        help_text="Character used for retrieving info",
        on_delete=models.deletion.PROTECT,
        related_name="+",
    )

    class Meta:
        default_permissions = ()

    def __str__(self):
        return (
            self.character.character.character_name
            + " ["
            + self.corporation.corporation_ticker
            + "]"
        )


class Location(models.Model):
    """ Location where the buyback program is operated at """

    name = models.CharField(
        max_length=32, help_text="Structure name where the contracts are accepted at"
    )

    eve_solar_system = models.ForeignKey(
        EveSolarSystem,
        help_text="System where the buyback structure is located",
        blank=True,
        default=None,
        null=True,
        on_delete=models.deletion.SET_DEFAULT,
        related_name="+",
    )

    def __str__(self):
        return self.eve_solar_system.name + " | " + self.name


class Program(models.Model):
    """An Eve Online buyback program"""

    owner = models.ForeignKey(
        Owner,
        help_text="Player that the contracts will be created for",
        on_delete=models.deletion.CASCADE,
        related_name="+",
    )

    is_corporation = models.BooleanField(
        default=False,
        help_text="Tick if contracts should be made to corporation instead of player.",
    )

    location = models.ForeignKey(
        Location,
        help_text="Solarystem and station name for contracts.",
        on_delete=models.deletion.CASCADE,
        related_name="+",
    )

    tax = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        help_text="Default tax is applied on all items unless an item spesific tax is assigned",
        validators=[MaxValueValidator(100), MinValueValidator(1)],
    )

    hauling_fuel_cost = models.IntegerField(
        default=0,
        help_text="ISK per m³ that will be removed from the buy price ie. to cover jump freighet fuel costs",
    )

    price_dencity_modifier = models.BooleanField(
        default=False,
        help_text="Should we modify buy prices for items with high volume and low value ie. T1 industrial hulls",
    )

    isk_cubic_treshold = models.IntegerField(
        default=0,
        null=True,
        help_text="At what ISK/m3 do we start to apply the low isk dencity tax. Tritanium is 500 ISK/m³ @ 5 ISK per unit price. PLEX is 14,5Trillion ISK/m³ @2.9M per unit price.",
    )

    isk_cubic_tax = models.IntegerField(
        default=0,
        null=True,
        help_text="How much tax do we apply on the low isk dencity items.",
        validators=[MaxValueValidator(100), MinValueValidator(1)],
    )

    allow_all_items = models.BooleanField(
        default=True,
        help_text="If true all items are accepted in this program with the default tax unless an item tax is spesified. Blueprints are not included in all items.",
    )

    use_refined_value = models.BooleanField(
        default=False,
        help_text="Take refined value into account when calculating prices for ore, ice and moon goo",
    )

    use_compressed_value = models.BooleanField(
        default=False,
        help_text="Take compressed value into account when calculating prices for ore, ice and moon goo",
    )

    use_raw_value = models.BooleanField(
        default=True,
        help_text="Take raw value into account when calculating prices for ore, ice and moon goo",
    )

    class Meta:
        default_permissions = ()


class ProgramItem(models.Model):
    """Items in the buyback program for a corp"""

    program = models.ForeignKey(
        Program,
        on_delete=models.deletion.CASCADE,
        help_text="What program do these items belong to",
    )
    item_type = models.ForeignKey(
        EveType,
        on_delete=models.deletion.CASCADE,
        help_text="Select item for special tax",
    )
    item_tax = models.IntegerField(
        default=0,
        null=True,
        help_text="How much tax do we add on top of the base tax for this item. Can also be negative.",
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )

    disallow_item = models.BooleanField(
        default=False,
        help_text="You can disallow an item from a buyback location. It will return 0 price if disallowed.",
    )

    class Meta:
        default_permissions = ()
        unique_together = ["program", "item_type"]

    def save(self, *args, **kwargs):
        if not self.item_tax:
            self.item_tax = self.program.tax
        super(ProgramItem, self).save(*args, **kwargs)


class ItemPrices(models.Model):
    buy = models.BigIntegerField()
    sell = models.BigIntegerField()
    updated = models.DateTimeField()
