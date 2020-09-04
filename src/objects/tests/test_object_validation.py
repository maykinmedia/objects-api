from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.models import Object

from .utils import mock_objecttype

OBJECT_TYPE = "https://example.com/objecttypes/v1/types/a6c109"


class ObjectValidationTests(APITestCase):
    @requests_mock.Mocker()
    def test_create_object_success(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(m, OBJECT_TYPE))

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "version": 1,
            "data": {"plantDate": "2020-04-12", "diameter": 30},
        }

        response = self.client.post(url, data)

        print(response)
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Object.objects.count(), 1)

        object_instance = Object.objects.get()

        self.assertEqual(
            object_instance.data, {"plantDate": "2020-04-12", "diameter": 30}
        )

    @requests_mock.Mocker()
    def test_create_object_invalid_objecttype_url(self, m):
        object_type_invalid = "https://example.com/objecttypes/v1/types/invalid"
        m.get(object_type_invalid, status_code=404)

        url = reverse("object-list")
        data = {
            "type": object_type_invalid,
            "version": 1,
            "data": {"plantDate": "2020-04-12",},
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    @requests_mock.Mocker()
    def test_create_object_no_version(self, m):
        m.get(
            OBJECT_TYPE,
            json={"url": OBJECT_TYPE, "name": "boom", "namePlural": "bomen",},
        )

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "version": 1,
            "data": {"plantDate": "2020-04-12", "diameter": 30},
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"],
            [f"{OBJECT_TYPE} doesn't include JSON schema for version 1"],
        )

    @requests_mock.Mocker()
    def test_create_object_schema_invalid(self, m):
        m.get(OBJECT_TYPE, json=mock_objecttype(m, OBJECT_TYPE))

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "version": 1,
            "data": {"plantDate": "2020-04-12",},
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"], ["'diameter' is a required property"]
        )
