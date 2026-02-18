from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factories import ObjectRecordFactory, ObjectTypeFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from .utils import reverse_lazy


class FilterObjectTypeTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )
        ObjectRecordFactory.create_batch(
            10, object__object_type=cls.object_type, start_at=date.today()
        )

    def test_list_with_default_page_size(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 10)
        self.assertIsNone(data["next"])

    def test_list_with_page_size_in_query(self):
        response = self.client.get(self.url, {"pageSize": 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 10)
        self.assertEqual(data["next"], f"http://testserver{self.url}?page=2&pageSize=5")
