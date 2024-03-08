from unittest.mock import patch

from django.test import TestCase, override_settings

import requests
import requests_mock
from django_setup_configuration.exceptions import SelfTestFailed
from zgw_consumers.constants import AuthTypes
from zgw_consumers.models import Service

from objects.config.objecttypes import ObjecttypesStep

from ..utils import mock_service_oas_get


@override_settings(
    OBJECTTYPES_API_ROOT="https://objecttypes.example.com/api/v2/",
    OBJECTTYPES_API_OAS="https://objecttypes.example.com/api/v2/schema/openapi.yaml",
    OBJECTS_OBJECTTYPES_TOKEN="some-random-string",
)
class ObjecttypesConfigurationTests(TestCase):
    def test_configure(self):
        configuration = ObjecttypesStep()

        configuration.configure()

        service = Service.objects.get(
            api_root="https://objecttypes.example.com/api/v2/"
        )
        self.assertEqual(
            service.oas, "https://objecttypes.example.com/api/v2/schema/openapi.yaml"
        )
        self.assertEqual(service.auth_type, AuthTypes.api_key)
        self.assertEqual(service.header_key, "Authorization")
        self.assertEqual(service.header_value, "Token some-random-string")

    @requests_mock.Mocker()
    def test_selftest_ok(self, m):
        configuration = ObjecttypesStep()
        configuration.configure()
        mock_service_oas_get(
            m, "https://objecttypes.example.com/api/v2/", "objecttypes"
        )
        m.get("https://objecttypes.example.com/api/v2/objecttypes", json={})

        configuration.test_configuration()

        self.assertEqual(
            m.last_request.url, "https://objecttypes.example.com/api/v2/objecttypes"
        )

    @requests_mock.Mocker()
    def test_selftest_fail(self, m):
        configuration = ObjecttypesStep()
        configuration.configure()
        mock_service_oas_get(
            m, "https://objecttypes.example.com/api/v2/", "objecttypes"
        )

        mock_kwargs = (
            {"exc": requests.ConnectTimeout},
            {"exc": requests.ConnectionError},
            {"status_code": 404},
            {"status_code": 403},
            {"status_code": 500},
        )
        for mock_config in mock_kwargs:
            with self.subTest(mock=mock_config):
                m.get(
                    "https://objecttypes.example.com/api/v2/objecttypes", **mock_config
                )

                with self.assertRaises(SelfTestFailed):
                    configuration.test_configuration()

    def test_is_configured(self):
        configuration = ObjecttypesStep()
        self.assertFalse(configuration.is_configured())

        configuration.configure()

        self.assertTrue(configuration.is_configured())
