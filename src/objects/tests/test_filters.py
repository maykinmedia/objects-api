from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.tests.factores import ObjectFactory, ObjectRecordFactory
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
        ObjectPermissionFactory(
            object_type=OTHER_OBJECT_TYPE,
            mode=PermissionModes.read_only,
            users=[cls.user],
        )

    def test_filter_object_type(self):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        ObjectRecordFactory.create(object=object)
        ObjectFactory.create(object_type=OTHER_OBJECT_TYPE)

        response = self.client.get(self.url, {"type": OBJECT_TYPE})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object.uuid])}",
        )


class FilterDataAttrsTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        ObjectPermissionFactory(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[cls.user]
        )

    def test_filter_exact_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "demo"}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            data={"name": "demo2"}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(data={}, object__object_type=OBJECT_TYPE)

        response = self.client.get(self.url, {"data_attrs": "name__exact__demo"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_exact_number(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(data={}, object__object_type=OBJECT_TYPE)

        response = self.client.get(self.url, {"data_attrs": "diameter__exact__4"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_lte(self):
        record1 = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=OBJECT_TYPE
        )
        record2 = ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(data={}, object__object_type=OBJECT_TYPE)

        response = self.client.get(self.url, {"data_attrs": "diameter__lte__5"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        data = sorted(data, key=lambda x: x["record"]["data"]["diameter"])

        self.assertEqual(len(data), 2)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record1.object.uuid])}",
        )
        self.assertEqual(
            data[1]["url"],
            f"http://testserver{reverse('object-detail', args=[record2.object.uuid])}",
        )

    def test_filter_lt(self):
        record = ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(data={}, object__object_type=OBJECT_TYPE)

        response = self.client.get(self.url, {"data_attrs": "diameter__lt__5"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_lte_not_numerical(self):
        response = self.client.get(self.url, {"data_attrs": "diameter__lt__value"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), ["Operator `lt` supports only numeric values"]
        )

    def test_filter_invalid_operator(self):
        response = self.client.get(self.url, {"data_attrs": "diameter__not__value"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), ["Comparison operator `not` is unknown"])

    def test_filter_invalid_param(self):
        response = self.client.get(self.url, {"data_attrs": "diameter__exact"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(), ["not enough values to unpack (expected 3, got 2)"]
        )

    def test_filter_nested_attr(self):
        record = ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 4}}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 5}}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(data={}, object__object_type=OBJECT_TYPE)

        response = self.client.get(
            self.url, {"data_attrs": "dimensions__diameter__exact__4"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_comma_separated(self):
        record = ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 4}, "name": "demo"},
            object__object_type=OBJECT_TYPE,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 5}, "name": "demo"},
            object__object_type=OBJECT_TYPE,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 4}, "name": "other"},
            object__object_type=OBJECT_TYPE,
        )

        response = self.client.get(
            self.url, {"data_attrs": "dimensions__diameter__exact__4,name__exact__demo"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )
