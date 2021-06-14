from django.contrib.gis.geos import Point

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factores import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory, TokenAuthFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS, POLYGON_AMSTERDAM_CENTRUM
from .utils import reverse, reverse_lazy

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


class TokenAuthTests(APITestCase):
    def setUp(self) -> None:
        object = ObjectFactory.create()
        self.urls = [
            reverse("object-list"),
            reverse("object-detail", args=[object.uuid]),
        ]

    def test_non_auth(self):
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token(self):
        TokenAuthFactory.create()
        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url, HTTP_AUTHORIZATION=f"Token 12345")
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)

    def test_retrieve_no_object_permission(self):
        object = ObjectFactory.create()
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_with_read_only_permission(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )
        object = ObjectFactory.create(object_type=self.object_type)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_history_no_object_permissions(self):
        object = ObjectFactory.create()
        url = reverse("object-history", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_history_with_read_only_permissions(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )
        object = ObjectFactory.create(object_type=self.object_type)
        url = reverse("object-history", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_read_only_perm(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )
        object = ObjectFactory.create(object_type=self.object_type)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.put(url, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_with_read_only_perm(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )
        object = ObjectFactory.create(object_type=self.object_type)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.patch(url, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_with_read_only_perm(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )
        object = ObjectFactory.create(object_type=self.object_type)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.delete(url, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_with_invalid_objecttype(self):
        url = reverse("object-list")
        data = {
            "type": "invalid-objecttype-url",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startDate": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_with_unknown_objecttype_service(self):
        url = reverse("object-list")
        data = {
            "type": "https://other-api.nl/v1/objecttypes/8be76be2-6567-4f5c-a17b-05217ab6d7b2",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startDate": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_with_unknown_objecttype_uuid(self):
        url = reverse("object-list")
        data = {
            "type": f"{OBJECT_TYPES_API}objecttypes/8be76be2-6567-4f5c-a17b-05217ab6d7b2",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startDate": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FilterAuthTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)

    def test_list_objects_without_object_permissions(self):
        ObjectFactory.create_batch(2)
        url = reverse_lazy("object-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_list_objects_limited_to_object_permission(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )
        object = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=object)
        ObjectFactory.create()
        url = reverse_lazy("object-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[object.uuid])}",
        )

    def test_search_objects_without_object_permissions(self):
        ObjectRecordFactory.create_batch(2, geometry=Point(4.905289, 52.369918))
        url = reverse("object-search")

        response = self.client.post(
            url,
            {
                "geometry": {
                    "within": {
                        "type": "Polygon",
                        "coordinates": [POLYGON_AMSTERDAM_CENTRUM],
                    }
                },
                "type": self.object_type.url,
            },
            **GEO_WRITE_KWARGS,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_search_objects_limited_to_object_permission(self):
        PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )
        record = ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918), object__object_type=self.object_type
        )
        ObjectRecordFactory.create(geometry=Point(4.905289, 52.369918))
        url = reverse("object-search")

        response = self.client.post(
            url,
            {
                "geometry": {
                    "within": {
                        "type": "Polygon",
                        "coordinates": [POLYGON_AMSTERDAM_CENTRUM],
                    }
                },
                "type": self.object_type.url,
            },
            **GEO_WRITE_KWARGS,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )
