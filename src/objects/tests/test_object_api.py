from datetime import date

from django.urls import reverse

import requests_mock
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.models import Object
from objects.core.tests.factores import ObjectFactory, ObjectRecordFactory

from .utils import mock_objecttype

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


@freeze_time("2020-08-08")
@requests_mock.Mocker()
class ObjectApiTests(APITestCase):
    def test_retrieve_object(self, m):
        object = ObjectFactory.create()
        object_record = ObjectRecordFactory.create(
            object=object, start_date=date.today()
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
                "type_version": object.version,
                "record": {
                    "data": object_record.data,
                    "start_date": object_record.start_date.isoformat(),
                    "end_date": object_record.end_date,
                    "registration_date": object_record.registration_date.isoformat(),
                    "correct": object_record.correct_id,
                },
            },
        )

    def test_create_object(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "type_version": 1,
            "record": {
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "start_date": "2020-01-01",
            },
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        object = Object.objects.get()

        self.assertEqual(object.object_type, OBJECT_TYPE)
        self.assertEqual(object.version, 1)

        record = object.records.get()

        self.assertEqual(record.data, {"plantDate": "2020-04-12", "diameter": 30})
        self.assertEqual(record.start_date, date(2020, 1, 1))
        self.assertEqual(record.registration_date, date(2020, 8, 8))
        self.assertIsNone(record.end_date)

    def test_update_object(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        initial_record = ObjectRecordFactory.create()
        object = initial_record.object

        assert initial_record.end_date is None

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": OBJECT_TYPE,
            "type_version": 1,
            "record": {
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "start_date": "2020-01-01",
                "correct": initial_record.id,
            },
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object.refresh_from_db()
        initial_record.refresh_from_db()

        self.assertEqual(object.object_type, OBJECT_TYPE)
        self.assertEqual(object.version, 1)
        self.assertEqual(object.records.count(), 2)

        current_record = object.current_record

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

    def test_patch_object_meta_info(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        initial_record = ObjectRecordFactory.create(
            data={"plantDate": "2020-04-12", "diameter": 30}
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": OBJECT_TYPE,
            "type_version": 1,
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object.refresh_from_db()

        self.assertEqual(object.object_type, OBJECT_TYPE)
        self.assertEqual(object.version, 1)
        self.assertEqual(object.records.count(), 1)
        self.assertEqual(object.last_record, initial_record)

    def test_patch_object_record(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        initial_record = ObjectRecordFactory.create()
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "record": {
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "start_date": "2020-01-01",
                "correct": initial_record.id,
            },
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        initial_record.refresh_from_db()

        self.assertEqual(object.records.count(), 2)

        current_record = object.current_record

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
        record = ObjectRecordFactory.create()
        object = record.object
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Object.objects.count(), 0)

    def test_history_object(self, m):
        record1 = ObjectRecordFactory.create(start_date=date(2020, 1, 1))
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
                    "id": record1.id,
                    "data": record1.data,
                    "start_date": record1.start_date.isoformat(),
                    "end_date": record2.start_date.isoformat(),
                    "registration_date": record1.registration_date.isoformat(),
                    "corrected": record2.id,
                },
                {
                    "id": record2.id,
                    "data": record2.data,
                    "start_date": record2.start_date.isoformat(),
                    "end_date": None,
                    "registration_date": date.today().isoformat(),
                    "corrected": None,
                },
            ],
        )
