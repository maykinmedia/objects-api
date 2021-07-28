import json

from django.contrib.gis.geos import Point

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factories import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS, POLYGON_AMSTERDAM_CENTRUM
from .utils import reverse, reverse_lazy

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


class RetrieveAuthFieldsTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)

    def test_retrieve_without_query(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record__startAt"]},
        )
        object = ObjectFactory.create(object_type=self.object_type)
        record = ObjectRecordFactory.create(
            object=object, data={"name": "some"}, version=1
        )
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{url}",
                "type": self.object_type.url,
                "record": {"startAt": record.start_at.isoformat()},
            },
        )
        self.assertEqual(
            set(response._headers["x-unauthorized-fields"][1].split(",")),
            {
                "uuid",
                "record__data__name",
                "record__correctionFor",
                "record__endAt",
                "record__correctedBy",
                "record__registrationAt",
                "record__index",
                "record__geometry__coordinates",
                "record__geometry__type",
                "record__typeVersion",
            },
        )

    def test_retrieve_with_query_fields(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record"]},
        )
        object = ObjectFactory.create(object_type=self.object_type)
        record = ObjectRecordFactory.create(object=object, version=1)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url, {"fields": "url,type,record__data__name"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{url}",
                "type": self.object_type.url,
                "record": {"data": {"name": record.data["name"]}},
            },
        )
        self.assertNotIn("x-unauthorized-fields", response._headers)

    def test_retrieve_incorrect_auth_fields(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "some"]},
        )
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=object, version=1)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            ["Fields in the configured authorization are absent in the data: 'some'"],
        )

    def test_retrieve_query_fields_not_allowed(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record__data__name"]},
        )
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(
            object=object, data={"name": "some", "desc": "some desc"}, version=1
        )
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url, {"fields": "url,type,record__data"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{url}",
                "record": {"data": {"name": "some"}},
                "type": self.object_type.url,
            },
        )
        self.assertEqual(
            response._headers["x-unauthorized-fields"][1], "record__data__desc"
        )

    def test_retrieve_no_allowed_fields(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"2": ["url", "type", "record"]},
        )
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(
            object=object, data={"name": "some", "desc": "some desc"}, version=1
        )
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {})
        self.assertIn("x-unauthorized-fields", response._headers)


class ListAuthFieldsTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        cls.other_object_type = ObjectTypeFactory()

    def test_list_without_query_different_object_types(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record"]},
        )
        PermissionFactory.create(
            object_type=self.other_object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "uuid", "record"]},
        )
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"name": "some"}, version=1
        )
        record2 = ObjectRecordFactory.create(
            object__object_type=self.other_object_type,
            data={"name": "other"},
            version=1,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "url": f"http://testserver{reverse('object-detail', args=[record2.object.uuid])}",
                    "uuid": str(record2.object.uuid),
                    "record": {
                        "index": record2.index,
                        "typeVersion": record2.version,
                        "data": {"name": "other"},
                        "geometry": json.loads(record2.geometry.json),
                        "startAt": record2.start_at.isoformat(),
                        "endAt": None,
                        "registrationAt": record2.registration_at.isoformat(),
                        "correctionFor": None,
                        "correctedBy": None,
                    },
                },
                {
                    "url": f"http://testserver{reverse('object-detail', args=[record1.object.uuid])}",
                    "type": self.object_type.url,
                    "record": {
                        "index": record1.index,
                        "typeVersion": record1.version,
                        "data": {"name": "some"},
                        "geometry": json.loads(record1.geometry.json),
                        "startAt": record1.start_at.isoformat(),
                        "endAt": None,
                        "registrationAt": record1.registration_at.isoformat(),
                        "correctionFor": None,
                        "correctedBy": None,
                    },
                },
            ],
        )
        self.assertEqual(
            response._headers["x-unauthorized-fields"][1],
            f"{self.other_object_type.url}(1)=type; {self.object_type.url}(1)=uuid",
        )

    def test_list_with_query_fields(self):
        other_object_type = ObjectTypeFactory()
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record"]},
        )
        PermissionFactory.create(
            object_type=other_object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "uuid", "record"]},
        )
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"name": "some"}, version=1
        )
        record2 = ObjectRecordFactory.create(
            object__object_type=other_object_type, data={"name": "other"}, version=1
        )

        response = self.client.get(self.url, {"fields": "url,record__data"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "url": f"http://testserver{reverse('object-detail', args=[record2.object.uuid])}",
                    "record": {
                        "data": {"name": "other"},
                    },
                },
                {
                    "url": f"http://testserver{reverse('object-detail', args=[record1.object.uuid])}",
                    "record": {
                        "data": {"name": "some"},
                    },
                },
            ],
        )
        self.assertNotIn("x-unauthorized-fields", response._headers)

    def test_list_incorrect_auth_fields(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "some", "record"]},
        )
        PermissionFactory.create(
            object_type=self.other_object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "uuid", "record"]},
        )
        ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"name": "some"}, version=1
        )
        ObjectRecordFactory.create(
            object__object_type=self.other_object_type,
            data={"name": "other"},
            version=1,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            ["Fields in the configured authorization are absent in the data: 'some'"],
        )

    def test_list_query_fields_not_allowed(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record"]},
        )
        PermissionFactory.create(
            object_type=self.other_object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "uuid", "record"]},
        )
        ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"name": "some"}
        )
        ObjectRecordFactory.create(
            object__object_type=self.other_object_type, data={"name": "other"}
        )

        response = self.client.get(self.url, {"fields": "uuid"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            ["'fields' query parameter has invalid or unauthorized values: 'uuid'"],
        )

    def test_list_no_allowed_fields(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"2": ["url", "type", "record"]},
        )
        PermissionFactory.create(
            object_type=self.other_object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"2": ["url", "uuid", "record"]},
        )
        ObjectRecordFactory.create(
            object__object_type=self.object_type, data={"name": "some"}, version=1
        )
        ObjectRecordFactory.create(
            object__object_type=self.other_object_type,
            data={"name": "other"},
            version=1,
        )
        url = reverse("object-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{}, {}])
        self.assertIn("x-unauthorized-fields", response._headers)


class SearchAuthFieldsTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-search")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)

    def test_search_with_fields_auth(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
            fields={"1": ["url", "type", "record__geometry"]},
        )
        record = ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918),
            object__object_type=self.object_type,
            data={"name": "some"},
            version=1,
        )
        response = self.client.post(
            self.url,
            data={
                "geometry": {
                    "within": {
                        "type": "Polygon",
                        "coordinates": [POLYGON_AMSTERDAM_CENTRUM],
                    }
                }
            },
            **GEO_WRITE_KWARGS,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            [
                {
                    "url": f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
                    "type": self.object_type.url,
                    "record": {
                        "geometry": {
                            "type": "Point",
                            "coordinates": [4.905289, 52.369918],
                        }
                    },
                }
            ],
        )
