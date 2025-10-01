from rest_framework import status
from rest_framework.test import APITestCase

from .utils import reverse


class APISchemaTest(APITestCase):
    def test_schema_endpoint(self):
        response = self.client.get(reverse("schema-redoc"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
