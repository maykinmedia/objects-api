from pathlib import Path

from django.test import TestCase

from django_setup_configuration.exceptions import PrerequisiteFailed
from django_setup_configuration.test_utils import execute_single_step
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory

from objects.setup_configuration.steps.objecttypes import (
    ObjectTypesConnectionConfigurationStep,
)

TEST_FILES = (Path(__file__).parent / "files").resolve()


class ObjectTypesConnectionConfigurationStepTests(TestCase):
    def test_create_connection(self):
        test_file_path = str(TEST_FILES / "objecttypes_connection.yaml")

        execute_single_step(
            ObjectTypesConnectionConfigurationStep, yaml_source=test_file_path
        )

        service = Service.objects.get(slug="objecttypes-api")

        self.assertEqual(service.label, "Objecttypen API")
        self.assertEqual(service.api_type, APITypes.orc)
        self.assertEqual(service.api_root, "https://objecttypes.nl/api/v1/")
        self.assertEqual(service.api_connection_check_path, "objecttypes")
        self.assertEqual(service.auth_type, AuthTypes.zgw)
        self.assertEqual(service.client_id, "client")
        self.assertEqual(service.secret, "secret")
        self.assertEqual(service.header_key, "Authorization")
        self.assertEqual(service.header_value, "Token foo")
        self.assertEqual(service.nlx, "http://some-outway-adress.local:8080/")
        self.assertEqual(service.user_id, "objects-api")
        self.assertEqual(service.user_representation, "Objects API")
        self.assertEqual(service.timeout, 60)

    def test_update_connection(self):
        test_file_path = str(TEST_FILES / "objecttypes_connection.yaml")

        service: Service = ServiceFactory(
            slug="objecttypes-api",
            label="Objecttypen API Test",
            api_type=APITypes.zrc,
            api_root="https://test.objecttypes.nl/api/v1/",
            api_connection_check_path="objecttype",
            auth_type=AuthTypes.api_key,
            client_id="test-client",
            secret="test-secret",
            header_key="authorization",
            header_value="Token foobar",
            nlx="http://test.some-outway-adress.local:8080/",
            user_id="test-objects-api",
            user_representation="Test Objects API",
            timeout=30,
        )

        execute_single_step(
            ObjectTypesConnectionConfigurationStep, yaml_source=test_file_path
        )

        self.assertEqual(Service.objects.count(), 1)

        service.refresh_from_db()

        self.assertEqual(service.label, "Objecttypen API")
        self.assertEqual(service.api_type, APITypes.orc)
        self.assertEqual(service.api_root, "https://objecttypes.nl/api/v1/")
        self.assertEqual(service.api_connection_check_path, "objecttypes")
        self.assertEqual(service.auth_type, AuthTypes.zgw)
        self.assertEqual(service.client_id, "client")
        self.assertEqual(service.secret, "secret")
        self.assertEqual(service.header_key, "Authorization")
        self.assertEqual(service.header_value, "Token foo")
        self.assertEqual(service.nlx, "http://some-outway-adress.local:8080/")
        self.assertEqual(service.user_id, "objects-api")
        self.assertEqual(service.user_representation, "Objects API")
        self.assertEqual(service.timeout, 60)

    def test_invalid_connection(self):
        test_file_path = str(TEST_FILES / "objecttypes_connection_invalid.yaml")

        with self.assertRaises(PrerequisiteFailed):
            execute_single_step(
                ObjectTypesConnectionConfigurationStep, yaml_source=test_file_path
            )

        self.assertEqual(Service.objects.count(), 0)

    def test_idempotent_step(self):
        test_file_path = str(TEST_FILES / "objecttypes_connection.yaml")

        execute_single_step(
            ObjectTypesConnectionConfigurationStep, yaml_source=test_file_path
        )

        service = Service.objects.get(slug="objecttypes-api")

        self.assertEqual(service.label, "Objecttypen API")
        self.assertEqual(service.api_type, APITypes.orc)
        self.assertEqual(service.api_root, "https://objecttypes.nl/api/v1/")
        self.assertEqual(service.api_connection_check_path, "objecttypes")
        self.assertEqual(service.auth_type, AuthTypes.zgw)
        self.assertEqual(service.client_id, "client")
        self.assertEqual(service.secret, "secret")
        self.assertEqual(service.header_key, "Authorization")
        self.assertEqual(service.header_value, "Token foo")
        self.assertEqual(service.nlx, "http://some-outway-adress.local:8080/")
        self.assertEqual(service.user_id, "objects-api")
        self.assertEqual(service.user_representation, "Objects API")
        self.assertEqual(service.timeout, 60)

        execute_single_step(
            ObjectTypesConnectionConfigurationStep, yaml_source=test_file_path
        )

        self.assertEqual(Service.objects.count(), 1)

        service.refresh_from_db()

        self.assertEqual(service.label, "Objecttypen API")
        self.assertEqual(service.api_type, APITypes.orc)
        self.assertEqual(service.api_root, "https://objecttypes.nl/api/v1/")
        self.assertEqual(service.api_connection_check_path, "objecttypes")
        self.assertEqual(service.auth_type, AuthTypes.zgw)
        self.assertEqual(service.client_id, "client")
        self.assertEqual(service.secret, "secret")
        self.assertEqual(service.header_key, "Authorization")
        self.assertEqual(service.header_value, "Token foo")
        self.assertEqual(service.nlx, "http://some-outway-adress.local:8080/")
        self.assertEqual(service.user_id, "objects-api")
        self.assertEqual(service.user_representation, "Objects API")
        self.assertEqual(service.timeout, 60)
