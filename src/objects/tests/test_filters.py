from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.tests.factores import ObjectFactory
from objects.utils.test import TokenAuthMixin

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/abc109"
OTHER_OBJECT_TYPE = "https://example.com/objecttypes/v1/types/qwe109"


class FilterTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        ObjectPermissionFactory(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[cls.user]
        )
        ObjectPermissionFactory(
            object_type=OTHER_OBJECT_TYPE,
            mode=PermissionModes.read_only,
            users=[cls.user],
        )

    def test_filter_object_type(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        ObjectFactory.create(object_type=OTHER_OBJECT_TYPE)

        response = self.client.get(self.url, {"type": OBJECT_TYPE})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object.uuid])}",
        )
