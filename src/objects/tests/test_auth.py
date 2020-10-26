from django.contrib.gis.geos import Point
from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.tests.factores import ObjectFactory, ObjectRecordFactory
from objects.utils.test import TokenAuthMixin

from .constants import GEO_WRITE_KWARGS, POLYGON_AMSTERDAM_CENTRUM

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


class TokenAuthTests(APITestCase):
    def test_non_auth(self):
        object = ObjectFactory.create()
        urls = [reverse("object-list"), reverse("object-detail", args=[object.uuid])]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(TokenAuthMixin, APITestCase):
    def test_retrieve_no_object_permission(self):
        object = ObjectFactory.create()
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_with_read_only_permission(self):
        ObjectPermissionFactory.create(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[self.user]
        )
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_history_no_object_permissions(self):
        object = ObjectFactory.create()
        url = reverse("object-history", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_history_with_read_only_permissions(self):
        ObjectPermissionFactory.create(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[self.user]
        )
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-history", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_read_only_perm(self):
        ObjectPermissionFactory.create(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[self.user]
        )
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.put(url, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_with_read_only_perm(self):
        ObjectPermissionFactory.create(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[self.user]
        )
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.patch(url, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_with_read_only_perm(self):
        ObjectPermissionFactory.create(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[self.user]
        )
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.delete(url, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FilterAuthTests(TokenAuthMixin, APITestCase):
    def test_list_objects_without_object_permissions(self):
        ObjectFactory.create_batch(2)
        url = reverse_lazy("object-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_list_objects_limited_to_object_permission(self):
        ObjectPermissionFactory.create(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[self.user]
        )
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
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
                "type": OBJECT_TYPE,
            },
            **GEO_WRITE_KWARGS,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_search_objects_limited_to_object_permission(self):
        ObjectPermissionFactory.create(
            object_type=OBJECT_TYPE, mode=PermissionModes.read_only, users=[self.user]
        )
        record = ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918), object__object_type=OBJECT_TYPE
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
                "type": OBJECT_TYPE,
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
