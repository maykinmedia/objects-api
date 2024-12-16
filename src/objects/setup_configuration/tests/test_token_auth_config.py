from pathlib import Path

from django.test import TestCase

from django_setup_configuration.exceptions import (
    ConfigurationRunFailed,
    PrerequisiteFailed,
)
from django_setup_configuration.test_utils import execute_single_step

from objects.setup_configuration.steps.token_auth import TokenAuthConfigurationStep
from objects.token.models import TokenAuth
from objects.token.tests.factories import TokenAuthFactory

DIR_FILES = (Path(__file__).parent / "files/token_auth").resolve()


class TokenAuthConfigurationStepTests(TestCase):
    def test_valid_setup_default(self):
        execute_single_step(
            TokenAuthConfigurationStep,
            yaml_source=str(DIR_FILES / "valid_setup_default.yaml"),
        )

        tokens = TokenAuth.objects.all()
        self.assertEqual(tokens.count(), 2)

        token = tokens.get(identifier="token-1")
        self.assertEqual(token.token, "18b2b74ef994314b84021d47b9422e82b685d82f")
        self.assertEqual(token.contact_person, "Person 1")
        self.assertEqual(token.email, "person-1@example.com")
        self.assertEqual(token.organization, "")
        self.assertEqual(token.application, "")
        self.assertEqual(token.administration, "")
        self.assertFalse(token.is_superuser)

        token = tokens.get(identifier="token-2")
        self.assertEqual(token.contact_person, "Person 2")
        self.assertEqual(token.token, "e882642bd0ec2482adcdc97258c2e6f98cb06d85")
        self.assertEqual(token.email, "person-2@example.com")
        self.assertEqual(token.organization, "")
        self.assertEqual(token.application, "")
        self.assertEqual(token.administration, "")
        self.assertFalse(token.is_superuser)

    def test_valid_setup_complete(self):
        execute_single_step(
            TokenAuthConfigurationStep,
            yaml_source=str(DIR_FILES / "valid_setup_complete.yaml"),
        )

        tokens = TokenAuth.objects.all()
        self.assertEqual(tokens.count(), 2)

        # Same as configuration
        token = tokens.get(identifier="token-1")
        self.assertEqual(token.token, "18b2b74ef994314b84021d47b9422e82b685d82f")
        self.assertEqual(token.contact_person, "Person 1")
        self.assertEqual(token.email, "person-1@example.com")
        self.assertEqual(token.organization, "Organization 1")
        self.assertEqual(token.application, "Application 1")
        self.assertEqual(token.administration, "Administration 1")
        self.assertTrue(token.is_superuser)

        # Token data updated
        token = tokens.get(identifier="token-2")
        self.assertEqual(token.contact_person, "Person 2")
        self.assertEqual(token.token, "e882642bd0ec2482adcdc97258c2e6f98cb06d85")
        self.assertEqual(token.email, "person-2@example.com")
        self.assertEqual(token.organization, "Organization 2")
        self.assertEqual(token.application, "Application 2")
        self.assertEqual(token.administration, "Administration 2")
        self.assertTrue(token.is_superuser)

    def test_valid_update_existing_tokens(self):
        TokenAuthFactory(
            identifier="token-1",
            token="18b2b74ef994314b84021d47b9422e82b685d82f",
            contact_person="Person 1",
            email="person-1@example.com",
            organization="Organization XYZ",
            application="Application XYZ",
            administration="Administration XYZ",
        )

        TokenAuthFactory(
            identifier="token-2",
            token="1cad42916dfa439af8c69000bf7b6af6a66782af",
            contact_person="Person 3",
            email="person-3@example.com",
        )
        execute_single_step(
            TokenAuthConfigurationStep,
            yaml_source=str(DIR_FILES / "valid_setup_complete.yaml"),
        )

        tokens = TokenAuth.objects.all()
        self.assertEqual(tokens.count(), 2)

        # Same as configuration
        token = tokens.get(identifier="token-1")
        self.assertEqual(token.token, "18b2b74ef994314b84021d47b9422e82b685d82f")
        self.assertEqual(token.contact_person, "Person 1")
        self.assertEqual(token.email, "person-1@example.com")
        self.assertEqual(token.organization, "Organization 1")
        self.assertEqual(token.application, "Application 1")
        self.assertEqual(token.administration, "Administration 1")
        self.assertTrue(token.is_superuser)

        # Token data updated
        token = tokens.get(identifier="token-2")
        self.assertEqual(token.contact_person, "Person 2")
        self.assertEqual(token.token, "e882642bd0ec2482adcdc97258c2e6f98cb06d85")
        self.assertEqual(token.email, "person-2@example.com")
        self.assertEqual(token.organization, "Organization 2")
        self.assertEqual(token.application, "Application 2")
        self.assertEqual(token.administration, "Administration 2")
        self.assertTrue(token.is_superuser)

        self.assertNotEqual(token.token, "1cad42916dfa439af8c69000bf7b6af6a66782af")
        self.assertNotEqual(token.contact_person, "Person 3")
        self.assertNotEqual(token.email, "person-3@example.com")

    def test_valid_idempotent_step(self):
        execute_single_step(
            TokenAuthConfigurationStep,
            yaml_source=str(DIR_FILES / "valid_setup_complete.yaml"),
        )

        tokens = TokenAuth.objects.all()
        self.assertEqual(tokens.count(), 2)

        old_token_a = tokens.get(identifier="token-1")
        self.assertEqual(old_token_a.identifier, "token-1")
        self.assertEqual(old_token_a.token, "18b2b74ef994314b84021d47b9422e82b685d82f")
        self.assertEqual(old_token_a.contact_person, "Person 1")
        self.assertEqual(old_token_a.email, "person-1@example.com")
        self.assertEqual(old_token_a.organization, "Organization 1")
        self.assertEqual(old_token_a.application, "Application 1")
        self.assertEqual(old_token_a.administration, "Administration 1")
        self.assertTrue(old_token_a.is_superuser)

        old_token_b = tokens.get(identifier="token-2")
        self.assertEqual(old_token_b.identifier, "token-2")
        self.assertEqual(old_token_b.contact_person, "Person 2")
        self.assertEqual(old_token_b.token, "e882642bd0ec2482adcdc97258c2e6f98cb06d85")
        self.assertEqual(old_token_b.email, "person-2@example.com")
        self.assertEqual(old_token_b.organization, "Organization 2")
        self.assertEqual(old_token_b.application, "Application 2")
        self.assertEqual(old_token_b.administration, "Administration 2")
        self.assertTrue(old_token_b.is_superuser)

        execute_single_step(
            TokenAuthConfigurationStep,
            yaml_source=str(DIR_FILES / "valid_setup_complete.yaml"),
        )

        tokens = TokenAuth.objects.all()
        self.assertEqual(tokens.count(), 2)

        new_token_a = tokens.get(identifier="token-1")
        self.assertEqual(new_token_a.identifier, old_token_a.identifier)
        self.assertEqual(new_token_a.token, old_token_a.token)
        self.assertEqual(new_token_a.contact_person, old_token_a.contact_person)
        self.assertEqual(new_token_a.email, old_token_a.email)
        self.assertEqual(new_token_a.organization, old_token_a.organization)
        self.assertEqual(new_token_a.application, old_token_a.application)
        self.assertEqual(new_token_a.administration, old_token_a.administration)

        new_token_b = tokens.get(identifier="token-2")
        self.assertEqual(new_token_b.identifier, old_token_b.identifier)
        self.assertEqual(new_token_b.contact_person, old_token_b.contact_person)
        self.assertEqual(new_token_b.token, old_token_b.token)
        self.assertEqual(new_token_b.email, old_token_b.email)
        self.assertEqual(new_token_b.organization, old_token_b.organization)
        self.assertEqual(new_token_b.application, old_token_b.application)
        self.assertEqual(new_token_b.administration, old_token_b.administration)

    def test_invalid_setup(self):
        with self.assertRaises(PrerequisiteFailed) as command_error:
            execute_single_step(
                TokenAuthConfigurationStep,
                yaml_source=str(DIR_FILES / "invalid_setup.yaml"),
            )

        self.assertTrue("Input should be a valid list" in str(command_error.exception))
        self.assertEqual(TokenAuth.objects.count(), 0)

    def test_invalid_setup_email(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "token-1",
                        "token": "ba9d233e95e04c4a8a661a27daffe7c9bd019067",
                        "contact_person": "Person 1",
                        "email": "invalid",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                ],
            },
        }
        with self.assertRaises(ConfigurationRunFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)

        self.assertTrue(
            "Validation error(s) occured for token-1" in str(command_error.exception)
        )
        self.assertEqual(TokenAuth.objects.count(), 0)

    def test_invalid_setup_token(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "token-1",
                        "token": "invalid token",
                        "contact_person": "Person 1",
                        "email": "person-1@example.com",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                ],
            },
        }
        with self.assertRaises(ConfigurationRunFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)

        self.assertTrue(
            "Validation error(s) occured for token-1" in str(command_error.exception)
        )
        self.assertEqual(TokenAuth.objects.count(), 0)

    def test_invalid_empty_token(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "token-1",
                        "token": "",
                        "contact_person": "Person 1",
                        "email": "person-1@example.com",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                ],
            },
        }
        with self.assertRaises(ConfigurationRunFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)

        self.assertTrue(
            "Validation error(s) occured for token-1" in str(command_error.exception)
        )
        self.assertEqual(TokenAuth.objects.count(), 0)

    def test_invalid_setup_token_missing(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "token-1",
                        "contact_person": "Person 1",
                        "email": "person-1@example.com",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                ],
            },
        }
        with self.assertRaises(PrerequisiteFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)

        self.assertTrue("Field required" in str(command_error.exception))
        self.assertEqual(TokenAuth.objects.count(), 0)

    def test_invalid_setup_token_unique(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "token-1",
                        "contact_person": "Person 1",
                        "token": "ba9d233e95e04c4a8a661a27daffe7c9bd019067",
                        "email": "person-1@example.com",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                    {
                        "identifier": "token-2",
                        "contact_person": "Person 2",
                        "token": "ba9d233e95e04c4a8a661a27daffe7c9bd019067",
                        "email": "person-2@example.com",
                        "organization": "Organization 2",
                        "application": "Application 2",
                        "administration": "Administration 2",
                    },
                ],
            },
        }
        with self.assertRaises(ConfigurationRunFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)

        self.assertTrue(
            "Failed configuring token token-2" in str(command_error.exception)
        )
        self.assertEqual(TokenAuth.objects.count(), 1)

    def test_invalid_setup_contact_person(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "token-1",
                        "token": "ba9d233e95e04c4a8a661a27daffe7c9bd019067",
                        "contact_person": "",
                        "email": "person-1@example.com",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                ],
            },
        }
        with self.assertRaises(ConfigurationRunFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)

        self.assertTrue(
            "Validation error(s) occured for token-1" in str(command_error.exception)
        )
        self.assertEqual(TokenAuth.objects.count(), 0)

    def test_invalid_setup_identifier(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "invalid identifier",
                        "token": "ba9d233e95e04c4a8a661a27daffe7c9bd019067",
                        "contact_person": "Person 1",
                        "email": "person-1@example.com",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                ],
            },
        }
        with self.assertRaises(PrerequisiteFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)
        self.assertTrue("String should match pattern" in str(command_error.exception))
        self.assertEqual(TokenAuth.objects.count(), 0)

    def test_invalid_empty_identifier(self):
        object_source = {
            "tokenauth_config_enable": True,
            "tokenauth": {
                "items": [
                    {
                        "identifier": "",
                        "token": "ba9d233e95e04c4a8a661a27daffe7c9bd019067",
                        "contact_person": "Person 1",
                        "email": "person-1@example.com",
                        "organization": "Organization 1",
                        "application": "Application 1",
                        "administration": "Administration 1",
                    },
                ],
            },
        }
        with self.assertRaises(PrerequisiteFailed) as command_error:
            execute_single_step(TokenAuthConfigurationStep, object_source=object_source)
        self.assertTrue("String should match pattern" in str(command_error.exception))
        self.assertEqual(TokenAuth.objects.count(), 0)