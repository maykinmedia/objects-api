from django.test import TestCase

from django_setup_configuration.exceptions import (
    ConfigurationException,
    PrerequisiteFailed,
)
from django_setup_configuration.test_utils import build_step_config_from_sources

from mozilla_django_oidc_db.models import OpenIDConnectConfig
from mozilla_django_oidc_db.setup_configuration.steps import AdminOIDCConfigurationStep

KEYCLOAK_BASE_URL = "http://localhost:8080/realms/test/protocol/openid-connect"


class AdminOIDCConfigurationTests(TestCase):

    def setUp(self):
        OpenIDConnectConfig.clear_cache()

    def test_execute_step(self):
        object_source = {
            "oidc_db_config_enable": True,
            "oidc_db_config_admin_auth": {
                "oidc_rp_client_id": "client-id",
                "oidc_rp_client_secret": "client-secret",
                "endpoint_config": {
                    "oidc_op_authorization_endpoint": f"{KEYCLOAK_BASE_URL}/auth",
                    "oidc_op_token_endpoint": f"{KEYCLOAK_BASE_URL}/token",
                    "oidc_op_user_endpoint": f"{KEYCLOAK_BASE_URL}/userinfo",
                },
            },
        }
        setup_config_model = build_step_config_from_sources(
            AdminOIDCConfigurationStep,
            object_source=object_source,
        )
        step = AdminOIDCConfigurationStep()
        step.execute(setup_config_model)

        config = OpenIDConnectConfig.get_solo()

        self.assertTrue(config.enabled)
        self.assertEqual(config.oidc_rp_client_id, "client-id")
        self.assertEqual(config.oidc_rp_client_secret, "client-secret")
        self.assertEqual(
            config.oidc_op_authorization_endpoint, f"{KEYCLOAK_BASE_URL}/auth"
        )
        self.assertEqual(config.oidc_op_token_endpoint, f"{KEYCLOAK_BASE_URL}/token")
        self.assertEqual(config.oidc_op_user_endpoint, f"{KEYCLOAK_BASE_URL}/userinfo")

        # Default mozilla_django_oidc_db configurations
        self.assertEqual(config.username_claim, ["sub"])
        self.assertEqual(config.groups_claim, ["roles"])
        self.assertEqual(
            config.claim_mapping,
            {
                "last_name": ["family_name"],
                "first_name": ["given_name"],
                "email": ["email"],
            },
        )

        self.assertEqual(config.default_groups.all().count(), 0)
        self.assertEqual(config.superuser_group_names, [])
        self.assertFalse(config.make_users_staff)

    def test_configuration_failed(self):
        with self.assertRaises(ConfigurationException):
            setup_config_model = build_step_config_from_sources(
                AdminOIDCConfigurationStep,
                yaml_source="",
            )
            AdminOIDCConfigurationStep().execute(setup_config_model)

        self.assertFalse(OpenIDConnectConfig.get_solo().enabled)

    def test_validate_requirements_failed(self):
        object_source = {
            "oidc_db_config_enable": True,
            "oidc_db_config_admin_auth": {
                "oidc_rp_client_id": "client-id",
                "oidc_rp_client_secret": "client-secret",
                "endpoint_config": {
                    "oidc_op_authorization_endpoint": "",
                    "oidc_op_token_endpoint": "",
                    "oidc_op_user_endpoint": "",
                },
            },
        }

        with self.assertRaises(PrerequisiteFailed):
            setup_config_model = build_step_config_from_sources(
                AdminOIDCConfigurationStep,
                object_source=object_source,
            )
            AdminOIDCConfigurationStep().execute(setup_config_model)

        self.assertFalse(OpenIDConnectConfig.get_solo().enabled)
