from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factores import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from .utils import reverse

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


class DynamicFieldsTests(TokenAuthMixin, APITestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def test_list_with_selected_fields(self):
        object_record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date.today()
        )
        object_record2 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date.today()
        )
        url = reverse("object-list")

        response = self.client.get(
            url, {"fields": "url,type,record__index,record__typeVersion"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(
            data,
            [
                {
                    "url": f"http://testserver{reverse('object-detail', args=[object_record2.object.uuid])}",
                    "type": self.object_type.url,
                    "record": {"index": 1, "typeVersion": object_record2.version},
                },
                {
                    "url": f"http://testserver{reverse('object-detail', args=[object_record1.object.uuid])}",
                    "type": self.object_type.url,
                    "record": {"index": 1, "typeVersion": object_record1.version},
                },
            ],
        )

    def test_retrieve_with_selected_fields(self):
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(
            object=object,
            start_at=date.today(),
            geometry="POINT (4.910649523925713 52.37240093589432)",
        )
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url, {"fields": "url,type,record__geometry"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                "url": f'http://testserver{reverse("object-detail", args=[object.uuid])}',
                "type": object.object_type.url,
                "record": {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [4.910649523925713, 52.37240093589432],
                    },
                },
            },
        )

    def test_fields_invalid(self):
        url = reverse("object-list")

        response = self.client.get(url, {"fields": "url,someField"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data, ["'fields' query parameter has invalid values: someField"]
        )
