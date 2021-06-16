from django.contrib.gis.geos import Point
from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.tests.factories import ObjectRecordFactory
from objects.utils.test import TokenAuthMixin

from .constants import GEO_WRITE_KWARGS, POLYGON_AMSTERDAM_CENTRUM

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"
OTHER_OBJECT_TYPE = "https://example.com/objecttypes/v1/types/qwe109"


class GeoSearchTests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("object-search")

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

    def test_filter_within(self):
        # in district
        record = ObjectRecordFactory.create(
            object__object_type=OBJECT_TYPE, geometry=Point(4.905289, 52.369918)
        )
        # outside of district
        ObjectRecordFactory.create(
            object__object_type=OBJECT_TYPE, geometry=Point(4.905650, 52.357621)
        )
        # no geo set
        ObjectRecordFactory.create(object__object_type=OBJECT_TYPE)

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
            f'http://testserver{reverse("object-detail", args=[record.object.uuid])}',
        )

    def test_filter_objecttype(self):
        record = ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918), object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918), object__object_type=OTHER_OBJECT_TYPE
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
                "type": OBJECT_TYPE,
            },
            **GEO_WRITE_KWARGS,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f'http://testserver{reverse("object-detail", args=[record.object.uuid])}',
        )
