from django.test import TestCase

from .testdata.factories import (
    ContractFactory,
    ContractItemFactory,
    ContractNotificationFactory,
    ItemPricesFactory,
    LocationFactory,
    OwnerFactory,
    ProgramFactory,
    ProgramItemFactory,
    TrackingFactory,
    TrackingItemFactory,
)
from .testdata.load_eveuniverse import load_eveuniverse


class TestOwners(TestCase):
    def test_should_have_str_method(self):
        # given
        obj = OwnerFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestLocations(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()

    def test_should_have_str_method(self):
        # given
        obj = LocationFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestProgram(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()

    def test_should_have_str_method(self):
        # given
        obj = ProgramFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestProgramItem(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()

    def test_should_have_str_method(self):
        # given
        obj = ProgramItemFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestItemPrices(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()

    def test_should_have_str_method(self):
        # given
        obj = ItemPricesFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestContracts(TestCase):
    def test_should_have_str_method(self):
        # given
        obj = ContractFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestContractItems(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()

    def test_should_have_str_method(self):
        # given
        obj = ContractItemFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestContractNotifications(TestCase):
    def test_should_have_str_method(self):
        # given
        obj = ContractNotificationFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestTrackings(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()

    def test_should_have_str_method(self):
        # given
        obj = TrackingFactory()
        # when/then
        self.assertIsInstance(str(obj), str)


class TestTrackingItems(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()

    def test_should_have_str_method(self):
        # given
        obj = TrackingItemFactory()
        # when/then
        self.assertIsInstance(str(obj), str)
