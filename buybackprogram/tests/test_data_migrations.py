from importlib import import_module
from django.test import TestCase
from .testdata.factories import ContractFactory, TrackingFactory, ProgramFactory
from .testdata.load_eveuniverse import load_eveuniverse
from django.apps import apps
from django.db import connection
from buybackprogram.models import Contract

data_migration = import_module(
    "buybackprogram.migrations.0011_delete_duplicated_contracts"
)


class TestDataMigration(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_eveuniverse()
        cls.program = ProgramFactory()

    def test_should_do_nothing_when_no_duplicates(self):
        # given
        contract = ContractFactory()
        # when
        data_migration.forwards(apps, connection.schema_editor())
        # then
        self.assertIn(contract, Contract.objects.all())

    def test_should_delete_duplicates(self):
        # given
        contract_1 = ContractFactory(contract_id=1)
        contract_2a = ContractFactory(contract_id=2, no_tracking=False)
        contract_2b = ContractFactory(contract_id=2, no_tracking=False)
        TrackingFactory(program=self.program, contract=contract_2a)
        # when
        data_migration.forwards(apps, connection.schema_editor())
        # then
        self.assertIn(contract_1, Contract.objects.all())
        self.assertIn(contract_2a, Contract.objects.all())
        self.assertNotIn(contract_2b, Contract.objects.all())

    def test_should_abort_when_duplicates_remain_after_deletion(self):
        # given
        contract_1 = ContractFactory(contract_id=1)  # noqa: F841
        contract_2a = ContractFactory(contract_id=2, no_tracking=False)
        contract_2b = ContractFactory(contract_id=2, no_tracking=False)  # noqa: F841
        contract_2c = ContractFactory(contract_id=2, no_tracking=True)  # noqa: F841
        TrackingFactory(program=self.program, contract=contract_2a)
        # when/then
        with self.assertRaises(SystemExit):
            data_migration.forwards(apps, connection.schema_editor())
