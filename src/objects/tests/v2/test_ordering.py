from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import get_validation_errors

from objects.core.tests.factories import ObjectRecordFactory, ObjectTypeFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from .utils import reverse_lazy

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


class OrderingTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)

        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_one_field_asc(self):
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 2)
        )
        record2 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 1)
        )
        record3 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 3)
        )

        response = self.client.get(self.url, {"ordering": "record__startAt"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["uuid"], str(record2.object.uuid))
        self.assertEqual(data[1]["uuid"], str(record1.object.uuid))
        self.assertEqual(data[2]["uuid"], str(record3.object.uuid))

    def test_one_field_desc(self):
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 2)
        )
        record2 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 1)
        )
        record3 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 3)
        )

        response = self.client.get(self.url, {"ordering": "-record__startAt"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["uuid"], str(record3.object.uuid))
        self.assertEqual(data[1]["uuid"], str(record1.object.uuid))
        self.assertEqual(data[2]["uuid"], str(record2.object.uuid))

    def test_several_fields(self):
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type,
            start_at=date(2020, 1, 1),
            index=2,
        )
        record2 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 1), index=1
        )
        record3 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at=date(2020, 1, 3), index=1
        )

        response = self.client.get(
            self.url, {"ordering": "-record__startAt,record__index"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["uuid"], str(record3.object.uuid))
        self.assertEqual(data[1]["uuid"], str(record2.object.uuid))
        self.assertEqual(data[2]["uuid"], str(record1.object.uuid))

    def test_json_field(self):
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"length": 4}
        )
        record2 = ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"length": 3}
        )
        record3 = ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"length": 5}
        )

        response = self.client.get(self.url, {"ordering": "record__data__length"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]["uuid"], str(record2.object.uuid))
        self.assertEqual(data[1]["uuid"], str(record1.object.uuid))
        self.assertEqual(data[2]["uuid"], str(record3.object.uuid))


class OrderingAllowedTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)

    def test_not_allowed_field(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record__startAt", "record__index"]},
        )

        response = self.client.get(self.url, {"ordering": "record__data__length"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        ordering_error = get_validation_errors(response, "")

        self.assertEqual(
            ordering_error["reason"],
            "You are not allowed to sort on following fields: record__data__length",
        )

    def test_allowed_field(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={
                "1": ["url", "uuid", "type", "record__index", "record__data"],
                "2": ["type", "uuid", "record__data"],
            },
        )
        PermissionFactory.create(
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["uuid", "record__data"]},
        )

        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"length": 4}, version=1
        )
        record2 = ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"length": 3}, version=1
        )

        response = self.client.get(self.url, {"ordering": "record__data__length"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["uuid"], str(record2.object.uuid))
        self.assertEqual(data[1]["uuid"], str(record1.object.uuid))
