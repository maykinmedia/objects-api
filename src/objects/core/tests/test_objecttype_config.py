from pathlib import Path

from django.db.models import QuerySet
from django.test import TestCase

from django_setup_configuration.exceptions import ConfigurationRunFailed
from django_setup_configuration.test_utils import execute_single_step
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory

from objects.core.models import ObjectType
from objects.core.tests.factories import ObjectTypeFactory
from objects.setup_configuration.steps.objecttypes import ObjectTypesConfigurationStep

TEST_FILES = (Path(__file__).parent / "files").resolve()


class ObjectTypesConfigurationStepTests(TestCase):
    def test_empty_database(self):
        service_1 = ServiceFactory(slug="service-1")
        service_2 = ServiceFactory(slug="service-2")

        test_file_path = str(TEST_FILES / "objecttypes_empty_database.yaml")

        execute_single_step(ObjectTypesConfigurationStep, yaml_source=test_file_path)

        objecttypes: QuerySet[ObjectType] = ObjectType.objects.order_by("_name")

        self.assertEqual(objecttypes.count(), 2)

        objecttype_1: ObjectType = objecttypes.first()

        self.assertEqual(str(objecttype_1.uuid), "b427ef84-189d-43aa-9efd-7bb2c459e281")
        self.assertEqual(objecttype_1._name, "Object Type 1")
        self.assertEqual(objecttype_1.service, service_1)

        objecttype_2: ObjectType = objecttypes.last()

        self.assertEqual(str(objecttype_2.uuid), "b0e8553f-8b1a-4d55-ab90-6d02f1bcf2c2")
        self.assertEqual(objecttype_2._name, "Object Type 2")
        self.assertEqual(objecttype_2.service, service_2)

    def test_existing_objecttype(self):
        test_file_path = str(TEST_FILES / "objecttypes_existing_objecttype.yaml")

        service_1: Service = ServiceFactory(slug="service-1")
        service_2: Service = ServiceFactory(slug="service-2")

        objecttype_1: ObjectType = ObjectTypeFactory(
            service=service_1,
            uuid="b427ef84-189d-43aa-9efd-7bb2c459e281",
            _name="Object Type 001",
        )
        objecttype_2: ObjectType = ObjectTypeFactory(
            service=service_2,
            uuid="b0e8553f-8b1a-4d55-ab90-6d02f1bcf2c2",
            _name="Object Type 002",
        )

        execute_single_step(ObjectTypesConfigurationStep, yaml_source=test_file_path)

        self.assertEqual(ObjectType.objects.count(), 3)

        objecttype_1.refresh_from_db()

        self.assertEqual(str(objecttype_1.uuid), "b427ef84-189d-43aa-9efd-7bb2c459e281")
        self.assertEqual(objecttype_1._name, "Object Type 1")
        self.assertEqual(objecttype_1.service, service_1)

        objecttype_2.refresh_from_db()

        self.assertEqual(str(objecttype_2.uuid), "b0e8553f-8b1a-4d55-ab90-6d02f1bcf2c2")
        self.assertEqual(objecttype_2._name, "Object Type 002")
        self.assertEqual(objecttype_2.service, service_2)

        objecttype_3: ObjectType = ObjectType.objects.get(
            uuid="7229549b-7b41-47d1-8106-414b2a69751b"
        )

        self.assertEqual(str(objecttype_3.uuid), "7229549b-7b41-47d1-8106-414b2a69751b")
        self.assertEqual(objecttype_3._name, "Object Type 3")
        self.assertEqual(objecttype_3.service, service_2)

    def test_unknown_service(self):
        service = ServiceFactory(slug="service-1")

        objecttype: ObjectType = ObjectTypeFactory(
            uuid="b427ef84-189d-43aa-9efd-7bb2c459e281",
            _name="Object Type 001",
            service=service,
        )

        test_file_path = str(TEST_FILES / "objecttypes_unknown_service.yaml")

        with self.assertRaises(ConfigurationRunFailed):
            execute_single_step(
                ObjectTypesConfigurationStep, yaml_source=test_file_path
            )

        self.assertEqual(ObjectType.objects.count(), 1)

        objecttype.refresh_from_db()

        self.assertEqual(str(objecttype.uuid), "b427ef84-189d-43aa-9efd-7bb2c459e281")
        self.assertEqual(objecttype._name, "Object Type 001")
        self.assertEqual(objecttype.service, service)

    def test_invalid_uuid(self):
        test_file_path = str(TEST_FILES / "objecttypes_invalid_uuid.yaml")

        service: Service = ServiceFactory(slug="service-1")

        objecttype: ObjectType = ObjectTypeFactory(
            service=service,
            uuid="b427ef84-189d-43aa-9efd-7bb2c459e281",
            _name="Object Type 001",
        )

        with self.assertRaises(ConfigurationRunFailed):
            execute_single_step(
                ObjectTypesConfigurationStep, yaml_source=test_file_path
            )

        self.assertEqual(ObjectType.objects.count(), 1)

        objecttype.refresh_from_db()

        self.assertEqual(str(objecttype.uuid), "b427ef84-189d-43aa-9efd-7bb2c459e281")
        self.assertEqual(objecttype._name, "Object Type 1")
        self.assertEqual(objecttype.service, service)

    def test_idempotent_step(self):
        service_1 = ServiceFactory(slug="service-1")
        service_2 = ServiceFactory(slug="service-2")

        test_file_path = str(TEST_FILES / "objecttypes_idempotent.yaml")

        execute_single_step(ObjectTypesConfigurationStep, yaml_source=test_file_path)

        objecttypes: QuerySet[ObjectType] = ObjectType.objects.order_by("_name")

        self.assertEqual(objecttypes.count(), 2)

        objecttype_1: ObjectType = objecttypes.first()

        self.assertEqual(str(objecttype_1.uuid), "b427ef84-189d-43aa-9efd-7bb2c459e281")
        self.assertEqual(objecttype_1._name, "Object Type 1")
        self.assertEqual(objecttype_1.service, service_1)

        objecttype_2: ObjectType = objecttypes.last()

        self.assertEqual(str(objecttype_2.uuid), "b0e8553f-8b1a-4d55-ab90-6d02f1bcf2c2")
        self.assertEqual(objecttype_2._name, "Object Type 2")
        self.assertEqual(objecttype_2.service, service_2)

        # Rerun
        execute_single_step(ObjectTypesConfigurationStep, yaml_source=test_file_path)

        objecttype_1.refresh_from_db()
        objecttype_2.refresh_from_db()

        self.assertEqual(ObjectType.objects.count(), 2)

        # objecttype 1
        self.assertEqual(str(objecttype_1.uuid), "b427ef84-189d-43aa-9efd-7bb2c459e281")
        self.assertEqual(objecttype_1._name, "Object Type 1")
        self.assertEqual(objecttype_1.service, service_1)

        # objecttype 2
        self.assertEqual(str(objecttype_2.uuid), "b0e8553f-8b1a-4d55-ab90-6d02f1bcf2c2")
        self.assertEqual(objecttype_2._name, "Object Type 2")
        self.assertEqual(objecttype_2.service, service_2)
