from unittest.mock import patch

from django.test import TestCase, override_settings

import requests
import requests_mock
from django_setup_configuration.exceptions import SelfTestFailed

from objects.config.demo import DemoUserStep
from objects.token.models import TokenAuth


@override_settings(
    DEMO_TOKEN="demo-random-string", DEMO_PERSON="Demo", DEMO_EMAIL="demo@demo.local"
)
class DemoConfigurationTests(TestCase):
    def test_configure(self):
        configuration = DemoUserStep()

        configuration.configure()

        token_auth = TokenAuth.objects.get()
        self.assertEqual(token_auth.token, "demo-random-string")
        self.assertTrue(token_auth.is_superuser)
        self.assertEqual(token_auth.contact_person, "Demo")
        self.assertEqual(token_auth.email, "demo@demo.local")

    @requests_mock.Mocker()
    @patch(
        "objects.config.demo.build_absolute_url",
        return_value="http://testserver/objects",
    )
    def test_configuration_check_ok(self, m, *mocks):
        configuration = DemoUserStep()
        configuration.configure()
        m.get("http://testserver/objects", json=[])

        configuration.test_configuration()

        self.assertEqual(m.last_request.url, "http://testserver/objects")
        self.assertEqual(m.last_request.method, "GET")

    @requests_mock.Mocker()
    @patch(
        "objects.config.demo.build_absolute_url",
        return_value="http://testserver/objects",
    )
    def test_configuration_check_failures(self, m, *mocks):
        configuration = DemoUserStep()
        configuration.configure()

        mock_kwargs = (
            {"exc": requests.ConnectTimeout},
            {"exc": requests.ConnectionError},
            {"status_code": 404},
            {"status_code": 403},
            {"status_code": 500},
        )
        for mock_config in mock_kwargs:
            with self.subTest(mock=mock_config):
                m.get("http://testserver/objects", **mock_config)

                with self.assertRaises(SelfTestFailed):
                    configuration.test_configuration()

    def test_is_configured(self):
        configuration = DemoUserStep()

        self.assertFalse(configuration.is_configured())

        configuration.configure()

        self.assertTrue(configuration.is_configured())
