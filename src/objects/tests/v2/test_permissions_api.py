from rest_framework import status
from rest_framework.test import APITestCase

from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from .utils import reverse


class ObjectApiTests(TokenAuthMixin, APITestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_list_permissions(self):
        permission1 = PermissionFactory.create(
            token_auth=self.token_auth,
            mode=PermissionModes.read_and_write,
        )
        permission2 = PermissionFactory.create(
            token_auth=self.token_auth,
            mode=PermissionModes.read_only,
            use_fields=True,
            fields={"1": ["url", "uuid"], "2": ["url", "record"]},
        )

        url = reverse("permission-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "type": f"http://testserver{reverse('objecttype-detail', args=[permission1.object_type.uuid])}",
                        "mode": PermissionModes.read_and_write,
                        "use_fields": False,
                        "fields": {},
                    },
                    {
                        "type": f"http://testserver{reverse('objecttype-detail', args=[permission2.object_type.uuid])}",
                        "mode": "read_only",
                        "use_fields": True,
                        "fields": {"1": ["url", "uuid"], "2": ["url", "record"]},
                    },
                ],
            },
        )

    def test_list_permissions_for_only_user(self):
        permission1 = PermissionFactory.create(
            token_auth=self.token_auth,
            mode=PermissionModes.read_and_write,
        )
        # permission for other token
        PermissionFactory.create(
            mode=PermissionModes.read_and_write,
        )

        url = reverse("permission-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data,
            [
                {
                    "type": f"http://testserver{reverse('objecttype-detail', args=[permission1.object_type.uuid])}",
                    "mode": PermissionModes.read_and_write,
                    "use_fields": False,
                    "fields": {},
                },
            ],
        )
