from datetime import date

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.tests.factories import ObjectRecordFactory
from objects.utils.test import TokenAuthMixin

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/abc109"
OTHER_OBJECT_TYPE = "https://example.com/objecttypes/v1/types/qwe109"


class FilterObjectTypeTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        ObjectPermissionFactory(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[cls.user]
        )
        ObjectRecordFactory.create_batch(
            10, object__object_type=OBJECT_TYPE, start_at=date.today()
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
