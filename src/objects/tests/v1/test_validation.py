import uuid

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.models import Object
from objects.core.tests.factores import ObjectRecordFactory, ObjectTypeFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from ..utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get
from .utils import reverse

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@requests_mock.Mocker()
class ObjectTypeValidationTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def test_create_object_with_not_found_objecttype_url(self, m):
        object_type_invalid = ObjectTypeFactory(service=self.object_type.service)
        PermissionFactory.create(
            object_type=object_type_invalid,
            mode=PermissionModes.read_and_write,
            token_auth=self.token_auth,
        )
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{object_type_invalid.url}/versions/1", status_code=404)

        url = reverse("object-list")
        data = {
            "type": object_type_invalid.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12"},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    def test_create_object_with_invalid_length(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        object_type_long = f"{OBJECT_TYPES_API}{'a'*1000}/{self.object_type.uuid}"
        data = {
            "type": object_type_long,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
            },
        }
        url = reverse("object-list")

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

        data = response.json()
        self.assertEqual(data["type"], ["The value has too many characters"])

    def test_create_object_no_version(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{self.object_type.url}/versions/10", status_code=404)

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
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
        self.assertEqual(
            data["non_field_errors"], ["Object type version can not be retrieved: None"]
        )

    def test_create_object_schema_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
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
            "type": self.object_type.url,
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.count(), 0)

    def test_create_object_correction_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        record = ObjectRecordFactory.create()
        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
                "correctionFor": record.index,
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Object.objects.exclude(id=record.object.id).count(), 0)

        data = response.json()
        self.assertEqual(
            data["record"]["correctionFor"],
            [f"Object with index={record.index} does not exist."],
        )

    def test_update_object_with_correction_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        corrected_record, initial_record = ObjectRecordFactory.create_batch(
            2, object__object_type=self.object_type
        )
        object = initial_record.object
        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
                "correctionFor": 5,
            },
        }

        response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["record"]["correctionFor"],
            ["Object with index=5 does not exist."],
        )

    def test_update_object_type_invalid(self, m):
        old_object_type = ObjectTypeFactory(service=self.object_type.service)
        PermissionFactory.create(
            object_type=old_object_type,
            mode=PermissionModes.read_and_write,
            token_auth=self.token_auth,
        )
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        initial_record = ObjectRecordFactory.create(
            object__object_type=old_object_type,
            data={"plantDate": "2020-04-12", "diameter": 30},
            version=1,
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": self.object_type.url,
        }

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["type"],
            ["This field can't be changed"],
        )

    def test_update_uuid_invalid(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        initial_record = ObjectRecordFactory.create(
            object__object_type=self.object_type
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {"uuid": uuid.uuid4()}

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(data["uuid"], ["This field can't be changed"])
