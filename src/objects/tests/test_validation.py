from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from objects.accounts.constants import PermissionModes
from objects.accounts.tests.factories import ObjectPermissionFactory
from objects.core.models import Object
from objects.core.tests.factores import ObjectRecordFactory
from objects.utils.test import TokenAuthMixin

from .constants import GEO_WRITE_KWARGS
from .utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"
OBJECT_TYPE = f"{OBJECT_TYPES_API}types/a6c109"


@requests_mock.Mocker()
class ObjectTypeValidationTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        Service.objects.create(api_type=APITypes.orc, api_root=OBJECT_TYPES_API)
        ObjectPermissionFactory(
            object_type=OBJECT_TYPE,
            mode=PermissionModes.read_and_write,
            users=[cls.user],
        )

    def test_create_object_invalid_objecttype_url(self, m):
        object_type_invalid = "https://example.com/objecttypes/v1/types/invalid"
        ObjectPermissionFactory(
            object_type=object_type_invalid,
            mode=PermissionModes.read_and_write,
            users=[self.user],
        )
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{object_type_invalid}/versions/1", status_code=404)

        url = reverse("object-list")
        data = {
            "type": object_type_invalid,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    def test_create_object_no_version(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPE}/versions/10", status_code=404)

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 10,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()
        self.assertEqual(data["non_field_errors"], ["Invalid input."])

    def test_create_object_schema_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPE}/versions/1", json=mock_objecttype_version(OBJECT_TYPE))

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"], ["'diameter' is a required property"]
        )

    def test_create_object_without_record_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")

        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    def test_create_object_correction_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPE}/versions/1", json=mock_objecttype_version(OBJECT_TYPE))

        record = ObjectRecordFactory.create()
        url = reverse("object-list")
        data = {
            "type": OBJECT_TYPE,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
                "correctionFor": record.uuid,
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.exclude(id=record.object.id).count(), 0)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"],
            ["Only records of the same objects can be corrected"],
        )

    def test_update_object_with_correction_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPE}/versions/1", json=mock_objecttype_version(OBJECT_TYPE))

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
                "startAt": "2020-01-01",
                "correctionFor": corrected_record.uuid,
            },
        }

        response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["non_field_errors"],
            ["Only records of the same objects can be corrected"],
        )

    def test_update_object_type_invalid(self, m):
        old_object_type = "https://example.com/objecttypes/v1/types/qwe109"
        ObjectPermissionFactory(
            object_type=old_object_type,
            mode=PermissionModes.read_and_write,
            users=[self.user],
        )
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(OBJECT_TYPE, json=mock_objecttype(OBJECT_TYPE))

        initial_record = ObjectRecordFactory.create(
            object__object_type=old_object_type,
            data={"plantDate": "2020-04-12", "diameter": 30},
            version=1,
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": OBJECT_TYPE,
        }

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["type"],
            ["This field can't be changed"],
        )
