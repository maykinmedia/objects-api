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

from .utils import reverse, reverse_lazy

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


class FilterObjectTypeTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        cls.another_object_type = ObjectTypeFactory(service=cls.object_type.service)

        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )
        PermissionFactory.create(
            object_type=cls.another_object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_object_type(self):
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=object)
        ObjectFactory.create(object_type=self.another_object_type)

        response = self.client.get(self.url, {"type": self.object_type.url})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object.uuid])}",
        )

    def test_filter_invalid_objecttype(self):
        response = self.client.get(self.url, {"type": "invalid-objecttype-url"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["type"], ["Invalid value."])

    def test_filter_unknown_objecttype(self):
        objecttype_url = (
            f"{OBJECT_TYPES_API}objecttypes/8be76be2-6567-4f5c-a17b-05217ab6d7b2"
        )
        response = self.client.get(self.url, {"type": objecttype_url})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["type"],
            [
                f"Select a valid object type. {objecttype_url} is not one of the available choices."
            ],
        )

    def test_filter_too_long_object_type(self):
        object_type_long = f"{OBJECT_TYPES_API}{'a'*1000}/{self.object_type.uuid}"
        response = self.client.get(self.url, {"type": object_type_long})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["type"], ["The value has too many characters"])


class FilterDataAttrsTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_exact_string(self):
        record = ObjectRecordFactory.create(
            data={"name": "demo"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"name": "demo2"}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

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
            data={"diameter": 4}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

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
            data={"diameter": 4}, object__object_type=self.object_type
        )
        record2 = ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

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
            data={"diameter": 4}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 5}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 6}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

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
            data={"dimensions": {"diameter": 4}}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 5}}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            data={"diameter": 4}, object__object_type=self.object_type
        )
        ObjectRecordFactory.create(data={}, object__object_type=self.object_type)

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
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 5}, "name": "demo"},
            object__object_type=self.object_type,
        )
        ObjectRecordFactory.create(
            data={"dimensions": {"diameter": 4}, "name": "other"},
            object__object_type=self.object_type,
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


class FilterDateTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_only,
            token_auth=cls.token_auth,
        )

    def test_filter_date_detail(self):
        object = ObjectFactory.create(object_type=self.object_type)
        record1 = ObjectRecordFactory.create(
            object=object, start_at="2020-01-01", end_at="2020-12-31"
        )
        record2 = ObjectRecordFactory.create(object=object, start_at="2021-01-01")

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"date": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["record"]["index"], record1.index)

    def test_filter_date_detail_no_actual_record(self):
        object = ObjectFactory.create(object_type=self.object_type)
        record = ObjectRecordFactory.create(object=object, start_at="2021-01-01")

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"date": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_date_list(self):
        # object 1 - show
        object1 = ObjectFactory.create(object_type=self.object_type)
        record11 = ObjectRecordFactory.create(
            object=object1, start_at="2020-01-01", end_at="2020-12-31"
        )
        record12 = ObjectRecordFactory.create(object=object1, start_at="2021-01-01")
        # object 2 - don't show
        record21 = ObjectRecordFactory.create(
            object__object_type=self.object_type, start_at="2021-01-01"
        )

        url = reverse_lazy("object-list")

        response = self.client.get(url, {"date": "2020-07-01"})

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object1.uuid])}",
        )
        self.assertEqual(data[0]["record"]["index"], record11.index)

    def test_filter_registration_date_detail(self):
        object = ObjectFactory.create(object_type=self.object_type)
        record1 = ObjectRecordFactory.create(
            object=object,
            registration_at="2020-01-01",
        )
        record2 = ObjectRecordFactory.create(
            object=object, registration_at="2021-01-01"
        )

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"registrationDate": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["record"]["index"], record1.index)

    def test_filter_registration_date_detail_no_record(self):
        object = ObjectFactory.create(object_type=self.object_type)
        record = ObjectRecordFactory.create(object=object, registration_at="2021-01-01")

        url = reverse_lazy("object-detail", args=[object.uuid])

        response = self.client.get(url, {"registrationDate": "2020-07-01"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_registration_date_list(self):
        # object 1 - show
        object1 = ObjectFactory.create(object_type=self.object_type)
        record11 = ObjectRecordFactory.create(
            object=object1, registration_at="2020-01-01"
        )
        record12 = ObjectRecordFactory.create(
            object=object1, registration_at="2021-01-01"
        )
        # object 2 - don't show
        record21 = ObjectRecordFactory.create(
            object__object_type=self.object_type, registration_at="2021-01-01"
        )

        url = reverse_lazy("object-list")

        response = self.client.get(url, {"registrationDate": "2020-07-01"})

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object1.uuid])}",
        )
        self.assertEqual(data[0]["record"]["index"], record11.index)

    def test_filter_on_both_date_and_registration_date(self):
        url = reverse_lazy("object-list")

        response = self.client.get(
            url, {"date": "2020-07-01", "registrationDate": "2020-08-01"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            [
                "'date' and 'registrationDate' parameters can't be used in the same request"
            ],
        )
