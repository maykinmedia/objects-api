from django.contrib.gis.geos import Point

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factories import ObjectRecordFactory, ObjectTypeFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS, POLYGON_AMSTERDAM_CENTRUM
from .utils import reverse, reverse_lazy


class GeoSearchTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-search")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        cls.another_object_type = ObjectTypeFactory.create()

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

    def test_filter_within(self):
        # in district
        record = ObjectRecordFactory.create(
            object__object_type=self.object_type, geometry=Point(4.905289, 52.369918)
        )
        # outside of district
        ObjectRecordFactory.create(
            object__object_type=self.object_type, geometry=Point(4.905650, 52.357621)
        )
        # no geo set
        ObjectRecordFactory.create(object__object_type=self.object_type)

        response = self.client.post(
            self.url,
            {
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

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_filter_objecttype(self):
        record = ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918), object__object_type=self.object_type
        )
        ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918),
            object__object_type=self.another_object_type,
        )

        response = self.client.post(
            self.url,
            {
                "geometry": {
                    "within": {
                        "type": "Polygon",
                        "coordinates": [POLYGON_AMSTERDAM_CENTRUM],
                    }
                },
                "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            },
            **GEO_WRITE_KWARGS,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )

    def test_without_geometry(self):
        record = ObjectRecordFactory.create(object__object_type=self.object_type)
        ObjectRecordFactory.create(object__object_type=self.another_object_type)
        response = self.client.post(
            self.url,
            {
                "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}"
            },
            **GEO_WRITE_KWARGS,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f"http://testserver{reverse('object-detail', args=[record.object.uuid])}",
        )
