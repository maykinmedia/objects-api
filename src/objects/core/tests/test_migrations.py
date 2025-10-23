import importlib
import threading
import time
from unittest.mock import patch

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.state import StateApps
from django.test import TransactionTestCase


# TODO move this to maykin common?
class BaseMigrationTest(TransactionTestCase):
    app: str
    migrate_from: str  # The migration before the one we want to test
    migrate_to: str  # The migration we want to test

    setting_overrides: dict = {}

    old_app_state: StateApps
    app_state: StateApps

    def setUp(self) -> None:
        """
        Setup the migration test by reversing to `migrate_from` state,
        then applying the `migrate_to` state.
        """
        assert self.app is not None, "You must define the `app` attribute"
        assert self.migrate_from is not None, "You must define `migrate_from`"
        assert self.migrate_to is not None, "You must define `migrate_to`"

        # Step 1: Set up the MigrationExecutor
        executor = MigrationExecutor(connection)

        # Step 2: Reverse to the starting migration state
        migrate_from = [(self.app, self.migrate_from)]
        old_migrate_state = executor.migrate(migrate_from)

        self.old_app_state = old_migrate_state.apps

    def _perform_migration(self) -> None:
        migrate_to = [(self.app, self.migrate_to)]

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload the graph in case of dependency changes
        executor.migrate(migrate_to)

        self.apps = executor.loader.project_state(migrate_to).apps

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        # reset to latest migration
        call_command("migrate", verbosity=0, database=connection._alias)


class TestBackfillDenormalizedObjectType(BaseMigrationTest):
    app = "core"
    migrate_from = "0032_objectrecord__object_type"
    migrate_to = "0033_objectrecord__backfill_denormalized_fields"

    def test_denormalize_object_type_to_object_record(self):
        ObjectType = self.old_app_state.get_model("core", "ObjectType")
        Object = self.old_app_state.get_model("core", "Object")
        ObjectRecord = self.old_app_state.get_model("core", "ObjectRecord")
        Service = self.old_app_state.get_model("zgw_consumers", "Service")

        service = Service.objects.create(api_root="http://example.local:8001/api/v2/")

        object_type1 = ObjectType.objects.create(
            uuid="5741f306-0b6d-4597-9bab-c7d5dafe6d75", service=service
        )
        object_type2 = ObjectType.objects.create(
            uuid="89a30410-5d80-4007-a660-50dd94994464", service=service
        )
        object1 = Object.objects.create(object_type=object_type1)
        object2 = Object.objects.create(object_type=object_type2)
        ObjectRecord.objects.create(
            object=object1, index=1, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object1, index=2, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object2, index=1, version=1, start_at="2025-01-01"
        )

        self._perform_migration()

        ObjectRecord = self.apps.get_model("core", "ObjectRecord")

        records = ObjectRecord.objects.order_by("pk")

        self.assertEqual(records.count(), 3)

        record1, record2, record3 = records

        self.assertEqual(record1._object_type, record1.object.object_type, object_type1)
        self.assertEqual(record2._object_type, record2.object.object_type, object_type1)
        self.assertEqual(record3._object_type, record3.object.object_type, object_type2)

    def test_concurrently_inserted_records_are_normalized(self):
        ObjectType = self.old_app_state.get_model("core", "ObjectType")
        Object = self.old_app_state.get_model("core", "Object")
        ObjectRecord = self.old_app_state.get_model("core", "ObjectRecord")
        Service = self.old_app_state.get_model("zgw_consumers", "Service")

        service = Service.objects.create(api_root="http://example.local:8001/api/v2/")

        object_type1 = ObjectType.objects.create(
            uuid="5741f306-0b6d-4597-9bab-c7d5dafe6d75", service=service
        )
        object_type2 = ObjectType.objects.create(
            uuid="89a30410-5d80-4007-a660-50dd94994464", service=service
        )
        object1 = Object.objects.create(object_type=object_type1)
        object2 = Object.objects.create(object_type=object_type2)
        ObjectRecord.objects.create(
            object=object1, index=1, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object1, index=2, version=1, start_at="2025-01-01"
        )
        ObjectRecord.objects.create(
            object=object2, index=1, version=1, start_at="2025-01-01"
        )

        migration_module = importlib.import_module(
            "objects.core.migrations.0033_objectrecord__backfill_denormalized_fields"
        )

        original_batch = migration_module.backfill_object_type_batch_concurrent

        def delayed_batch(cursor):
            time.sleep(0.1)  # simulate long-running batch
            return original_batch(cursor)

        with patch.object(
            migration_module,
            "backfill_object_type_batch_concurrent",
            side_effect=delayed_batch,
        ):
            thread = threading.Thread(target=self._perform_migration)
            thread.start()

            # Simultaneously insert a new record
            ObjectRecord.objects.create(
                object=object2,
                index=2,
                version=1,
                start_at="2025-01-01",
                _object_type=None,
            )

            thread.join()

        ObjectRecord = self.apps.get_model("core", "ObjectRecord")

        records = ObjectRecord.objects.order_by("pk")

        self.assertEqual(records.count(), 4)

        record1, record2, record3, record4 = records

        self.assertEqual(record1._object_type, record1.object.object_type, object_type1)
        self.assertEqual(record2._object_type, record2.object.object_type, object_type1)
        self.assertEqual(record3._object_type, record3.object.object_type, object_type2)
        # Assert that the inserted row was also backfilled
        self.assertEqual(record4._object_type, record4.object.object_type, object_type2)
