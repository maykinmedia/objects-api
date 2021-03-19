from django.core.management import call_command
from django.test import TestCase


class GenerateSchemaTests(TestCase):
    def test_generate_schema(self):
        """src/manage.py generate_swagger \
            ./src/swagger2.0.json \
            --overwrite \
            --format=json \
            --mock-request \
            --url https://example.com/api/v1"""
        result = call_command(
            "generate_swagger",
            "swagger2.0.json",
            overwrite=True,
            format="json",
            mock_request=True,
            url="https://example.com/api/v1",
        )
