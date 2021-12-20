from typing import Tuple

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from esi.errors import TokenExpiredError, TokenInvalidError
from esi.models import Token
from eveuniverse.models import EveSolarSystem, EveType

from allianceauth.authentication.models import CharacterOwnership, State

# Create your models here.
from allianceauth.eveonline.models import EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger

from buybackprogram.app_settings import BUYBACKPROGRAM_TRACKING_PREFILL

from .decorators import fetch_token_for_owner
from .providers import esi

logger = get_extension_logger(__name__)


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app and see own statics."),
            (
                "manage_programs",
                "Can manage own buyback programs and see own program statics.",
            ),
            ("see_all_statics", "Can see all program statics."),
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

    user = models.ForeignKey(
        User,
        help_text="User that manages the program",
        on_delete=models.deletion.PROTECT,
        related_name="+",
    )

    class Meta:
        default_permissions = ()

    @fetch_token_for_owner(
        [
            "esi-contracts.read_character_contracts.v1",
            "esi-contracts.read_corporation_contracts.v1",
        ]
    )
    def update_contracts_esi(self, token):

        logger.debug("Fetching contracts for %s" % self.character)

        contracts = self._fetch_contracts()

        for contract in contracts:

            # Only get contracts with the correct prefill ticker
            if BUYBACKPROGRAM_TRACKING_PREFILL in contract["title"]:
                obj, created = Contract.objects.update_or_create(
                    assignee_id=contract["assignee_id"],
                    availability=contract["availability"],
                    contract_id=contract["contract_id"],
                    date_completed=contract["date_completed"],
                    date_expired=contract["date_expired"],
                    date_issued=contract["date_issued"],
                    for_corporation=contract["for_corporation"],
                    issuer_corporation_id=contract["issuer_corporation_id"],
                    issuer_id=contract["issuer_id"],
                    price=contract["price"],
                    status=contract["status"],
                    title=contract["title"],
                    volume=contract["volume"],
                    defaults={"contract_id": contract["contract_id"]},
                )

                # If we created an new contract
                if created:
                    logger.debug(
                        "New contract %s created. Starting item fetch"
                        % contract["contract_id"]
                    )

                    character_id = self.character.character.character_id

                    contract_items = esi.client.Contracts.get_characters_character_id_contracts_contract_id_items(
                        character_id=character_id,
                        contract_id=contract["contract_id"],
                        token=token.valid_access_token(),
                    ).results()

                    for item in contract_items:

                        cont = Contract.objects.get(contract_id=contract["contract_id"])
                        itm = EveType.objects.get(pk=item["type_id"])

                        obj, created = ContractItem.objects.update_or_create(
                            contract=cont,
                            eve_type=itm,
                            quantity=item["quantity"],
                            defaults={"contract": cont},
                        )

                    logger.debug(
                        "Updated items for contract %s" % contract["contract_id"]
                    )
                else:
                    logger.debug("Contract %s updated." % contract["contract_id"])

        logger.debug("Fetching corporation contracts for %s" % self.character)

        contracts = self._fetch_corporation_contracts()

        for contract in contracts:

            # Only get contracts with the correct prefill ticker
            if BUYBACKPROGRAM_TRACKING_PREFILL in contract["title"]:
                obj, created = Contract.objects.update_or_create(
                    assignee_id=contract["assignee_id"],
                    availability=contract["availability"],
                    contract_id=contract["contract_id"],
                    date_completed=contract["date_completed"],
                    date_expired=contract["date_expired"],
                    date_issued=contract["date_issued"],
                    for_corporation=contract["for_corporation"],
                    issuer_corporation_id=contract["issuer_corporation_id"],
                    issuer_id=contract["issuer_id"],
                    price=contract["price"],
                    status=contract["status"],
                    title=contract["title"],
                    volume=contract["volume"],
                    defaults={"contract_id": contract["contract_id"]},
                )

                if created:
                    logger.debug(
                        "New corporation contract %s created. Starting item fetch"
                        % contract["contract_id"]
                    )

                    corporation_id = self.character.character.corporation_id

                    contract_items = esi.client.Contracts.get_corporations_corporation_id_contracts_contract_id_items(
                        corporation_id=corporation_id,
                        contract_id=contract["contract_id"],
                        token=token.valid_access_token(),
                    ).results()

                    for item in contract_items:

                        cont = Contract.objects.get(contract_id=contract["contract_id"])
                        itm = EveType.objects.get(pk=item["type_id"])

                        obj, created = ContractItem.objects.update_or_create(
                            contract=cont,
                            eve_type=itm,
                            quantity=item["quantity"],
                            defaults={"contract": cont},
                        )

                    logger.debug(
                        "Updated items for corporation contract %s"
                        % contract["contract_id"]
                    )
                else:
                    logger.debug(
                        "Corporation contract %s updated." % contract["contract_id"]
                    )

    @fetch_token_for_owner(["esi-contracts.read_character_contracts.v1"])
    def _fetch_contracts(self, token) -> list:

        character_id = self.character.character.character_id

        contracts = esi.client.Contracts.get_characters_character_id_contracts(
            character_id=character_id,
            token=token.valid_access_token(),
        ).results()

        return contracts

    @fetch_token_for_owner(["esi-contracts.read_corporation_contracts.v1"])
    def _fetch_corporation_contracts(self, token) -> list:

        corporation_id = self.character.character.corporation_id

        contracts = esi.client.Contracts.get_corporations_corporation_id_contracts(
            corporation_id=corporation_id,
            token=token.valid_access_token(),
        ).results()

        return contracts

    def token(self, scopes=None) -> Tuple[Token, int]:
        """returns a valid Token for the owner"""
        token = None
        error = None

        # abort if character is not configured
        if self.character is None:
            logger.error("%s: No character configured to sync", self)
            error = self.ERROR_NO_CHARACTER

        # abort if character does not have sufficient permissions
        elif self.corporation and not self.character.user.has_perm(
            "buybackprogram.manage_programs"
        ):
            logger.error(
                "%s: This character does not have sufficient permission to sync contracts",
                self,
            )
            error = self.ERROR_INSUFFICIENT_PERMISSIONS

        # abort if character does not have sufficient permissions
        elif not self.character.user.has_perm("buybackprogram.manage_programs"):
            logger.error(
                "%s: This character does not have sufficient permission to sync contracts",
                self,
            )
            error = self.ERROR_INSUFFICIENT_PERMISSIONS

        else:
            try:
                # get token
                token = (
                    Token.objects.filter(
                        user=self.character.user,
                        character_id=self.character.character.character_id,
                    )
                    .require_scopes(scopes)
                    .require_valid()
                    .first()
                )
            except TokenInvalidError:
                logger.error("%s: Invalid token for fetching calendars", self)
                error = self.ERROR_TOKEN_INVALID
            except TokenExpiredError:
                logger.error("%s: Token expired for fetching calendars", self)
                error = self.ERROR_TOKEN_EXPIRED
            else:
                if not token:
                    logger.error("%s: No token found with sufficient scopes", self)
                    error = self.ERROR_TOKEN_INVALID

        return token, error

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
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )

    hauling_fuel_cost = models.IntegerField(
        default=0,
        help_text="ISK per m³ that will be removed from the buy price ie. to cover jump freighet fuel costs. <b>Should not be used with price dencity modifier</b>",
    )

    price_dencity_modifier = models.BooleanField(
        default=False,
        help_text="Should we modify buy prices for items with high volume and low value ie. T1 industrial hulls. <b>Should not be used with hauling fuel cost</b>",
    )

    price_dencity_treshold = models.IntegerField(
        default=0,
        null=True,
        help_text="At what ISK/m3 do we start to apply the low isk dencity tax. Tritanium is 500 ISK/m³ @ 5 ISK per unit price. PLEX is 14,5Trillion ISK/m³ @2.9M per unit price.",
    )

    price_dencity_tax = models.IntegerField(
        default=0,
        null=True,
        help_text="How much tax do we apply on the low isk dencity items.",
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )

    allow_all_items = models.BooleanField(
        default=True,
        help_text="If true all items are accepted to the buyback program. You can set extra taxes or disallow individual items from the program item section. If set to false you need to add each accepted item into the program item section. Blueprints are not included in all items.",
    )

    use_refined_value = models.BooleanField(
        default=False,
        help_text="Take refined value into account when calculating prices for ore, ice and moon goo",
    )

    use_compressed_value = models.BooleanField(
        default=False,
        help_text="Take compressed value into account when calculating prices for ore, ice and moon goo",
    )

    use_raw_ore_value = models.BooleanField(
        default=True,
        help_text="Take raw ore value into account when calculating prices for ore, ice and moon goo",
    )

    allow_unpacked_items = models.BooleanField(
        default=False,
        help_text="Do you want to allow unpacked items in this program such as assembled ship hulls?",
    )

    refining_rate = models.IntegerField(
        default=0,
        null=True,
        help_text="Refining rate to be used if refined value is active",
        validators=[MaxValueValidator(100), MinValueValidator(0)],
    )

    restricted_to_group = models.ManyToManyField(
        Group,
        blank=True,
        related_name="buybackprogram_require_groups",
        help_text="The group(s) that will be able to see this buyback program. If none is selected program is open for all.",
    )
    restricted_to_state = models.ManyToManyField(
        State,
        blank=True,
        related_name="buybackprogram_require_states",
        help_text="The state(s) that will be able to see this buyback program. If none is selected program is open for all.",
    )

    class Meta:
        default_permissions = ()

    def clean(self):
        super().clean()
        if (
            self.allow_all_items
            and not self.use_refined_value
            and not self.use_compressed_value
            and not self.use_raw_ore_value
        ):
            raise ValidationError(
                "All items are allowed but not a single pricing method for ores is selected. Please use at least one pricing method for ores if all items is allowed."
            )
        if self.price_dencity_modifier and not self.price_dencity_tax:
            raise ValidationError(
                "Price dencity is used but value for price dencity tax is missing"
            )
        if self.price_dencity_modifier and not self.price_dencity_treshold:
            raise ValidationError(
                "Price dencity is used but value for price dencity treshold is missing"
            )
        if self.use_refined_value and not self.refining_rate:
            raise ValidationError(
                "Refined value is used for ore pricing method but no refining rate is provided. Provide a refining rate to used with this pricing model."
            )


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
    eve_type = models.OneToOneField(
        EveType,
        on_delete=models.deletion.CASCADE,
        unique=True,
    )
    buy = models.BigIntegerField()
    sell = models.BigIntegerField()
    updated = models.DateTimeField()


class Tracking(models.Model):
    program = models.ForeignKey(
        Program,
        null=True,
        on_delete=models.deletion.SET_NULL,
        related_name="+",
    )
    issuer_user = models.ForeignKey(
        User,
        on_delete=models.deletion.CASCADE,
        related_name="+",
    )
    value = models.BigIntegerField(null=False)
    taxes = models.BigIntegerField(null=False)
    hauling_cost = models.BigIntegerField(null=False)
    donation = models.BigIntegerField(null=True, blank=True)
    net_price = models.BigIntegerField(null=False)
    tracking_number = models.CharField(max_length=20)


class TrackingItem(models.Model):

    tracking = models.ForeignKey(
        Tracking,
        on_delete=models.deletion.CASCADE,
        help_text="What tracking do these items belong to",
    )

    eve_type = models.ForeignKey(
        EveType,
        on_delete=models.deletion.CASCADE,
        help_text="Item type information",
    )

    buy_value = models.BigIntegerField(null=False)

    quantity = models.IntegerField()


class Contract(models.Model):

    assignee_id = models.IntegerField()
    availability = models.CharField(max_length=20)
    contract_id = models.IntegerField()
    date_completed = models.DateTimeField(null=True)
    date_expired = models.DateTimeField(null=True)
    date_issued = models.DateTimeField()
    for_corporation = models.BooleanField()
    issuer_corporation_id = models.IntegerField()
    issuer_id = models.IntegerField()
    price = models.BigIntegerField()
    status = models.CharField(max_length=30)
    title = models.CharField(max_length=128)
    volume = models.BigIntegerField()


class ContractItem(models.Model):

    contract = models.ForeignKey(
        Contract,
        on_delete=models.deletion.CASCADE,
        help_text="What contract do these items belong to",
    )

    eve_type = models.ForeignKey(
        EveType,
        on_delete=models.deletion.CASCADE,
        help_text="Item type information",
    )

    quantity = models.IntegerField()
