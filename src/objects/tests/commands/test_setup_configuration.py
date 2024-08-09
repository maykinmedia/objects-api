from io import StringIO

from django.contrib.sites.models import Site
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings
from django.urls import reverse

import requests_mock
from rest_framework import status
from zgw_consumers.models import Service

from objects.config.demo import DemoUserStep
from objects.config.objecttypes import ObjecttypesStep
from objects.config.site import SiteConfigurationStep

from ..utils import mock_service_oas_get


@override_settings(
    OBJECTS_DOMAIN="objects.example.com",
    OBJECTS_ORGANIZATION="ACME",
    OBJECTTYPES_API_ROOT="https://objecttypes.example.com/api/v2/",
    OBJECTTYPES_API_OAS="https://objecttypes.example.com/api/v2/schema/openapi.yaml",
    OBJECTS_OBJECTTYPES_TOKEN="some-random-string",
    DEMO_CONFIG_ENABLE=True,
    DEMO_TOKEN="demo-random-string",
    DEMO_PERSON="Demo",
    DEMO_EMAIL="demo@demo.local",
)
class SetupConfigurationTests(TestCase):
    def setUp(self):
        super().setUp()

        self.addCleanup(Site.objects.clear_cache)

    @requests_mock.Mocker()
    def test_setup_configuration(self, m):
        stdout = StringIO()
        # mocks
        m.get("http://objects.example.com/", status_code=200)
        m.get("http://objects.example.com/api/v2/objects", json=[])
        mock_service_oas_get(
            m, "https://objecttypes.example.com/api/v2/", "objecttypes"
        )
        m.get("https://objecttypes.example.com/api/v2/objecttypes", json={})

        call_command("setup_configuration", stdout=stdout)

        with self.subTest("Command output"):
            command_output = stdout.getvalue().splitlines()
            expected_output = [
                f"Configuration will be set up with following steps: [{SiteConfigurationStep()}, "
                f"{ObjecttypesStep()}, {DemoUserStep()}]",
                f"Configuring {SiteConfigurationStep()}...",
                f"{SiteConfigurationStep()} is successfully configured",
                f"Configuring {ObjecttypesStep()}...",
                f"{ObjecttypesStep()} is successfully configured",
                f"Configuring {DemoUserStep()}...",
                f"{DemoUserStep()} is successfully configured",
                f"Instance configuration completed.",
            ]

            self.assertEqual(command_output, expected_output)

        with self.subTest("Site configured correctly"):
            site = Site.objects.get_current()
            self.assertEqual(site.domain, "objects.example.com")
            self.assertEqual(site.name, "Objects ACME")

        with self.subTest("Objects can query Objecttypes API"):
            client = Service.get_client("https://objecttypes.example.com/api/v2/")
            self.assertIsNotNone(client)

            client.list("objecttype")

            list_call = m.last_request
            self.assertEqual(
                list_call.url, "https://objecttypes.example.com/api/v2/objecttypes"
            )
            self.assertIn("Authorization", list_call.headers)
            self.assertEqual(
                list_call.headers["Authorization"], "Token some-random-string"
            )

        with self.subTest("Demo user configured correctly"):
            response = self.client.get(
                reverse("v2:object-list"),
                HTTP_AUTHORIZATION="Token demo-random-string",
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    @requests_mock.Mocker()
    def test_setup_configuration_selftest_fails(self, m):
        m.get("http://objects.example.com/", status_code=500)
        m.get("http://objects.example.com/api/v2/objects", status_code=200)
        mock_service_oas_get(
            m, "https://objecttypes.example.com/api/v2/", "objecttypes"
        )
        m.get("https://objecttypes.example.com/api/v2/objecttypes", json={})

        with self.assertRaisesMessage(
            CommandError,
            "Configuration test failed with errors: "
            "Site Configuration: Could not access home page at 'http://objects.example.com/'",
        ):
            call_command("setup_configuration")

    @requests_mock.Mocker()
    def test_setup_configuration_without_selftest(self, m):
        stdout = StringIO()

        call_command("setup_configuration", no_selftest=True, stdout=stdout)
        command_output = stdout.getvalue()

        self.assertEqual(len(m.request_history), 0)
        self.assertTrue("Selftest is skipped" in command_output)
