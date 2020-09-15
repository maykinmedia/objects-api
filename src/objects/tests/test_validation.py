from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.models import Object
from objects.core.tests.factores import ObjectRecordFactory

from .utils import mock_objecttype

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


@requests_mock.Mocker()
class ObjectTypeValidationTests(APITestCase):
    def test_create_object_invalid_objecttype_url(self, m):
        object_type_invalid = "https://example.com/objecttypes/v1/types/invalid"
        m.get(object_type_invalid, status_code=404)

        url = reverse("object-list")
        data = {
            "type": object_type_invalid,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startDate": "2020-01-01",
            },
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    def test_create_object_no_version(self, m):
        m.get(
            OBJECT_TYPE,
            json={"url": OBJECT_TYPE, "name": "boom", "namePlural": "bomen",},
        )

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startDate": "2020-01-01",
            },
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"],
            [f"{OBJECT_TYPE} doesn't include JSON schema for version 1"],
        )

    def test_create_object_schema_invalid(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startDate": "2020-01-01",
            },
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"], ["'diameter' is a required property"]
        )

    def test_create_object_without_record_invalid(self, m):
        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    def test_create_object_correction_invalid(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        record = ObjectRecordFactory.create()
        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startDate": "2020-01-01",
                "correct": record.id,
            },
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.exclude(id=record.object.id).count(), 0)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"],
            ["Only records of the same objects can be corrected"],
        )

    def test_update_object_with_correction_invalid(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        corrected_record, initial_record = ObjectRecordFactory.create_batch(
            2, object__object_type=OBJECT_TYPE
        )
        object = initial_record.object
        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startDate": "2020-01-01",
                "correct": corrected_record.id,
            },
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"],
            ["Only records of the same objects can be corrected"],
        )

    def test_update_object_type_invalid(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        initial_record = ObjectRecordFactory.create(
            data={"plantDate": "2020-04-12", "diameter": 30}, version=1,
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": OBJECT_TYPE,
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["type"], ["This field can't be changed"],
        )
