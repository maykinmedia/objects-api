from io import StringIO

from django.core.management import CommandError, call_command
from django.test import TestCase

from objects.token.models import TokenAuth


class GenerateTokenCommandTests(TestCase):
    def test_token_created_with_required_args(self):
        out = StringIO()
        contact_person = "John Doe"
        email = "john@example.com"

        call_command(
            "generate_token",
            contact_person,
            email,
            stdout=out,
        )

        self.assertEqual(TokenAuth.objects.count(), 1)
        token = TokenAuth.objects.first()
        self.assertEqual(token.contact_person, contact_person)
        self.assertEqual(token.email, email)
        self.assertEqual(token.organization, "")
        self.assertIn("Token", out.getvalue())

    def test_token_created_with_all_optional_args(self):
        out = StringIO()
        call_command(
            "generate_token",
            "Alice Smith",
            "alice@example.com",
            "--organization",
            "Acme Inc",
            "--application",
            "WeatherApp",
            "--administration",
            "City Council",
            stdout=out,
        )

        token = TokenAuth.objects.get(email="alice@example.com")
        self.assertEqual(token.contact_person, "Alice Smith")
        self.assertEqual(token.organization, "Acme Inc")
        self.assertEqual(token.application, "WeatherApp")
        self.assertEqual(token.administration, "City Council")
        self.assertIn("Token", out.getvalue())

    def test_missing_required_arguments(self):
        with self.assertRaises(CommandError):
            call_command("generate_token")

    def test_stdout_contains_token(self):
        out = StringIO()
        call_command("generate_token", "Bob", "bob@example.com", stdout=out)
        output = out.getvalue()
        self.assertIn("Token", output)
        self.assertIn(TokenAuth.objects.first().token, output)

    def test_duplicate_email_allowed_with_unique_identifier(self):
        TokenAuth.objects.create(
            contact_person="Bob", email="bob@example.com", identifier="unique-1"
        )
        out = StringIO()
        call_command("generate_token", "Bob", "bob@example.com", stdout=out)

        self.assertEqual(TokenAuth.objects.filter(email="bob@example.com").count(), 2)
