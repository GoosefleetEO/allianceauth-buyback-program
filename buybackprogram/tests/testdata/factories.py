import datetime as dt

import factory
import factory.fuzzy
from app_utils.testdata_factories import EveCorporationInfoFactory, UserMainFactory
from buybackprogram.models import (
    Contract,
    ContractItem,
    ContractNotification,
    ItemPrices,
    Location,
    Owner,
    Program,
    ProgramItem,
    Tracking,
    TrackingItem,
)
from django.utils.timezone import now
from eveuniverse.models import EveSolarSystem, EveType


def random_eve_type() -> EveType:
    return EveType.objects.filter(published=True).order_by("?").first()


class UserProjectManagerFactory(UserMainFactory):
    main_character__scopes = [
        "esi-contracts.read_character_contracts.v1",
        "esi-contracts.read_corporation_contracts.v1",
        "esi-universe.read_structures.v1",
    ]
    permissions__ = ["buybackprogram.basic_access", "buybackprogram.manage_programs"]


class UserIssuerFactory(UserMainFactory):
    main_character__scopes = [
        "esi-contracts.read_character_contracts.v1",
        "esi-contracts.read_corporation_contracts.v1",
        "esi-universe.read_structures.v1",
    ]
    permissions__ = ["buybackprogram.basic_access"]


class OwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Owner

    user = factory.SubFactory(UserProjectManagerFactory)
    character = factory.lazy_attribute(
        lambda o: o.user.profile.main_character.character_ownership
    )

    @factory.lazy_attribute
    def corporation(self):
        return EveCorporationInfoFactory(
            corporation_id=self.user.profile.main_character.corporation_id
        )


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Faker("word")
    owner = factory.SubFactory(OwnerFactory)

    @factory.lazy_attribute
    def eve_solar_system(self):
        obj = EveSolarSystem.objects.order_by("?").first()
        if not obj:
            raise RuntimeError("No EveSolarSystem found for LocationFactory.")
        return obj


class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program

    name = factory.Faker("sentence")
    owner = factory.SubFactory(OwnerFactory)

    @factory.post_generation
    def location(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for obj in extracted:
                self.location.add(obj)
        else:
            obj = LocationFactory()
            self.location.add(obj)


class ProgramItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProgramItem

    program = factory.SubFactory(ProgramFactory)

    @factory.lazy_attribute
    def item_type(self):
        obj = random_eve_type()
        if not obj:
            raise RuntimeError("No EveType found for ProgramItemFactory.")
        return obj


class ItemPricesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ItemPrices

    buy = factory.fuzzy.FuzzyInteger(1, 10_000_000)
    sell = factory.fuzzy.FuzzyInteger(1, 10_000_000)
    updated = factory.lazy_attribute(lambda o: now())

    @factory.lazy_attribute
    def eve_type(self):
        obj = random_eve_type()
        if not obj:
            raise RuntimeError("No EveType found for ProgramItemFactory.")
        return obj


class ContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contract

    assignee_id = factory.fuzzy.FuzzyInteger(90_000, 99_000)
    availability = "public"
    contract_id = factory.fuzzy.FuzzyInteger(1_000_000_000, 2_000_000_000)
    date_issued = factory.fuzzy.FuzzyDateTime(now() - dt.timedelta(days=3))
    for_corporation = False
    issuer_corporation_id = factory.fuzzy.FuzzyInteger(90_000, 99_000)
    issuer_id = factory.fuzzy.FuzzyInteger(90_000, 99_000)
    price = factory.fuzzy.FuzzyInteger(90_000, 99_000)
    status = "outstanding"
    title = factory.Faker("sentence")
    volume = factory.fuzzy.FuzzyInteger(10, 320)


class ContractItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContractItem

    contract = factory.SubFactory(ContractFactory)
    quantity = factory.fuzzy.FuzzyInteger(1, 99)

    @factory.lazy_attribute
    def eve_type(self):
        obj = random_eve_type()
        if not obj:
            raise RuntimeError("No EveType found for ProgramItemFactory.")
        return obj


class ContractNotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContractNotification

    contract = factory.SubFactory(ContractFactory)
    icon = factory.Faker("url")
    color = factory.fuzzy.FuzzyChoice(["green", "orange", "red"])
    message = factory.Faker("sentence")


class TrackingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tracking

    program = factory.SubFactory(ProgramFactory)
    issuer_user = factory.SubFactory(UserIssuerFactory)
    value = factory.fuzzy.FuzzyInteger(1_000_000, 100_000_000)
    taxes = factory.fuzzy.FuzzyInteger(1_000_000, 5_000_000)
    net_price = factory.fuzzy.FuzzyInteger(1_000_000, 100_000_000)
    hauling_cost = factory.fuzzy.FuzzyInteger(1_000_000, 5_000_000)
    tracking_number = 5  # what is this?
    created_at = factory.fuzzy.FuzzyDateTime(now() - dt.timedelta(days=3))


class TrackingItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TrackingItem

    tracking = factory.SubFactory(TrackingFactory)
    buy_value = factory.fuzzy.FuzzyInteger(1_000_000, 100_000_000)
    quantity = factory.fuzzy.FuzzyInteger(1, 999)

    @factory.lazy_attribute
    def eve_type(self):
        obj = random_eve_type()
        if not obj:
            raise RuntimeError("No EveType found for ProgramItemFactory.")
        return obj
