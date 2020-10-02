from django.contrib.gis.geos import Point
from django.urls import reverse, reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factores import ObjectRecordFactory

from .constants import POLYGON_AMSTERDAM_CENTRUM
from .utils import GEO_WRITE_KWARGS

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


class GeoSearchTests(APITestCase):
    url = reverse_lazy("object-search")

    def test_filter_within(self):
        # in district
        record = ObjectRecordFactory.create(geometry=Point(4.905289, 52.369918))
        # outside of district
        ObjectRecordFactory.create(geometry=Point(4.905650, 52.357621))
        # no geo set
        ObjectRecordFactory.create()

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

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f'http://testserver{reverse("object-detail", args=[record.object.uuid])}',
        )

    def test_filter_objecttype(self):
        record = ObjectRecordFactory.create(
            geometry=Point(4.905289, 52.369918), object__object_type=OBJECT_TYPE
        )
        ObjectRecordFactory.create(geometry=Point(4.905289, 52.369918))

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

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["url"],
            f'http://testserver{reverse("object-detail", args=[record.object.uuid])}',
        )
