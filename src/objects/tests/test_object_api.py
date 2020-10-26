import json
from datetime import date

from django.urls import reverse

import requests_mock
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.models import Object
from objects.core.tests.factores import ObjectFactory, ObjectRecordFactory
from objects.utils.test import TokenAuthMixin

from .constants import GEO_WRITE_KWARGS
from .utils import mock_objecttype

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


@freeze_time("2020-08-08")
@requests_mock.Mocker()
class ObjectApiTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        ObjectPermissionFactory(
            object_type=OBJECT_TYPE,
            mode=PermissionModes.read_and_write,
            users=[cls.user],
        )

    def test_retrieve_object(self, m):
        object = ObjectFactory.create(object_type=OBJECT_TYPE)
        object_record = ObjectRecordFactory.create(
            object=object,
            start_date=date.today(),
            geometry="POINT (4.910649523925713 52.37240093589432)",
        )
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                "url": f'http://testserver{reverse("object-detail", args=[object.uuid])}',
                "type": object.object_type,
                "record": {
                    "uuid": str(object_record.uuid),
                    "typeVersion": object_record.version,
                    "data": object_record.data,
                    "geometry": json.loads(object_record.geometry.json),
                    "startDate": object_record.start_date.isoformat(),
                    "endDate": object_record.end_date,
                    "registrationDate": object_record.registration_date.isoformat(),
                    "correct": None,
                },
            },
        )

    def test_create_object(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startDate": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        object = Object.objects.get()

        self.assertEqual(object.object_type, OBJECT_TYPE)

        record = object.records.get()

        self.assertEqual(record.version, 1)
        self.assertEqual(record.data, {"plantDate": "2020-04-12", "diameter": 30})
        self.assertEqual(record.start_date, date(2020, 1, 1))
        self.assertEqual(record.registration_date, date(2020, 8, 8))
        self.assertEqual(record.geometry.coords, (4.910649523925713, 52.37240093589432))
        self.assertIsNone(record.end_date)

    def test_update_object(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        initial_record = ObjectRecordFactory.create(object__object_type=OBJECT_TYPE)
        object = initial_record.object

        assert initial_record.end_date is None

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": object.object_type,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startDate": "2020-01-01",
                "correct": initial_record.uuid,
            },
        }

        response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object.refresh_from_db()
        initial_record.refresh_from_db()

        self.assertEqual(object.object_type, OBJECT_TYPE)
        self.assertEqual(object.records.count(), 2)

        current_record = object.current_record

        self.assertEqual(current_record.version, 1)
        self.assertEqual(
            current_record.data, {"plantDate": "2020-04-12", "diameter": 30}
        )
        self.assertEqual(
            current_record.geometry.coords, (4.910649523925713, 52.37240093589432)
        )
        self.assertEqual(current_record.start_date, date(2020, 1, 1))
        self.assertEqual(current_record.registration_date, date(2020, 8, 8))
        self.assertIsNone(current_record.end_date)
        self.assertEqual(current_record.correct, initial_record)
        # assert changes to initial record
        self.assertNotEqual(current_record, initial_record)
        self.assertEqual(initial_record.corrected, current_record)
        self.assertEqual(initial_record.end_date, date(2020, 1, 1))

    def test_patch_object_record(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        initial_record = ObjectRecordFactory.create(
            version=1, object__object_type=OBJECT_TYPE, start_date=date.today()
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "record": {
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startDate": "2020-01-01",
                "correct": initial_record.uuid,
            },
        }

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        initial_record.refresh_from_db()

        self.assertEqual(object.records.count(), 2)

        current_record = object.current_record

        self.assertEqual(current_record.version, initial_record.version)
        self.assertEqual(
            current_record.data, {"plantDate": "2020-04-12", "diameter": 30}
        )
        self.assertEqual(current_record.start_date, date(2020, 1, 1))
        self.assertEqual(current_record.registration_date, date(2020, 8, 8))
        self.assertIsNone(current_record.end_date)
        self.assertEqual(current_record.correct, initial_record)
        # assert changes to initial record
        self.assertNotEqual(current_record, initial_record)
        self.assertEqual(initial_record.corrected, current_record)
        self.assertEqual(initial_record.end_date, date(2020, 1, 1))

    def test_delete_object(self, m):
        record = ObjectRecordFactory.create(object__object_type=OBJECT_TYPE)
        object = record.object
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Object.objects.count(), 0)

    def test_history_object(self, m):
        record1 = ObjectRecordFactory.create(
            object__object_type=OBJECT_TYPE,
            start_date=date(2020, 1, 1),
            geometry="POINT (4.910649523925713 52.37240093589432)",
        )
        object = record1.object
        record2 = ObjectRecordFactory.create(
            object=object, start_date=date.today(), correct=record1
        )
        url = reverse("object-history", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            [
                {
                    "uuid": str(record1.uuid),
                    "typeVersion": record1.version,
                    "data": record1.data,
                    "geometry": json.loads(record1.geometry.json),
                    "startDate": record1.start_date.isoformat(),
                    "endDate": record2.start_date.isoformat(),
                    "registrationDate": record1.registration_date.isoformat(),
                    "corrected": str(record2.uuid),
                },
                {
                    "uuid": str(record2.uuid),
                    "typeVersion": record2.version,
                    "data": record2.data,
                    "geometry": None,
                    "startDate": record2.start_date.isoformat(),
                    "endDate": None,
                    "registrationDate": date.today().isoformat(),
                    "corrected": None,
                },
            ],
        )
