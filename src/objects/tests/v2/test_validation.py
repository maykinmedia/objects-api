import datetime
import uuid

from django.conf import settings

import requests
import requests_mock
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.tests import get_validation_errors

from objects.core.models import Object
from objects.core.tests.factories import ObjectRecordFactory, ObjectTypeFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import ClearCachesMixin, TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from ..utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get
from .utils import reverse

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@requests_mock.Mocker()
class ObjectTypeValidationTests(TokenAuthMixin, ClearCachesMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def test_valid_create_object_check_cache(self, m):
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
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2020-01-01",
            },
        }
        with self.subTest("ok_cache"):
            self.assertEqual(m.call_count, 0)
            self.assertEqual(Object.objects.count(), 0)
            for n in range(5):
                self.client.post(url, data, **GEO_WRITE_KWARGS)
            # just one request should run — the first one
            self.assertEqual(m.call_count, 1)
            self.assertEqual(Object.objects.count(), 5)

        with self.subTest("clear_cache"):
            m.reset_mock()
            self.assertEqual(m.call_count, 0)
            for n in range(5):
                self._clear_caches()
                self.client.post(url, data, **GEO_WRITE_KWARGS)
            self.assertEqual(m.call_count, 5)
            self.assertEqual(Object.objects.count(), 10)

        with self.subTest("cache_timeout"):
            m.reset_mock()
            self._clear_caches()
            old_datetime = datetime.datetime(2025, 5, 1, 12, 0)
            with freeze_time(old_datetime.isoformat()):
                self.assertEqual(m.call_count, 0)
                self.client.post(url, data, **GEO_WRITE_KWARGS)
                self.client.post(url, data, **GEO_WRITE_KWARGS)
                # only one request for two post
                self.assertEqual(m.call_count, 1)

            # cache_timeout is still ok
            cache_timeout = settings.OBJECTTYPE_VERSION_CACHE_TIMEOUT
            new_datetime = old_datetime + datetime.timedelta(
                seconds=(cache_timeout - 60)
            )
            with freeze_time(new_datetime.isoformat()):
                # same request as before
                self.assertEqual(m.call_count, 1)
                self.client.post(url, data, **GEO_WRITE_KWARGS)
                # same request as before
                self.assertEqual(m.call_count, 1)

            # cache_timeout is expired
            cache_timeout = settings.OBJECTTYPE_VERSION_CACHE_TIMEOUT
            new_datetime = old_datetime + datetime.timedelta(
                seconds=(cache_timeout + 60)
            )
            with freeze_time(new_datetime.isoformat()):
                # same request as before
                self.assertEqual(m.call_count, 1)
                self.client.post(url, data, **GEO_WRITE_KWARGS)
                # new request
                self.assertEqual(m.call_count, 2)

    def test_create_object_with_not_found_objecttype_url(self, m):
        object_type_invalid = ObjectTypeFactory.create(service=self.object_type.service)
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
        object_type_long = f"{OBJECT_TYPES_API}{'a' * 1000}/{self.object_type.uuid}"
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

        self.assertEqual(data["status"], 400)
        self.assertEqual(Object.objects.count(), 0)

        type_error = get_validation_errors(response, "type")

        self.assertEqual(type_error["code"], "max_length")
        self.assertEqual(
            type_error["reason"],
            "The value has too many characters",
        )

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

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "Object type version can not be retrieved.",
        )

    def test_create_object_objecttype_request_error(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{self.object_type.url}/versions/10", exc=requests.HTTPError)

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

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "Object type version can not be retrieved.",
        )

    def test_create_object_objecttype_with_no_jsonSchema(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/10",
            status_code=200,
            json={"key": "value"},
        )

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

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            f"{self.object_type.versions_url} does not appear to be a valid objecttype.",
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

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "'diameter' is a required property",
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

        error = get_validation_errors(response, "record.correctionFor")

        self.assertEqual(
            error["reason"],
            f"Object with index={record.index} does not exist.",
        )

    def test_create_object_geometry_not_allowed(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(
            self.object_type.url,
            json=mock_objecttype(self.object_type.url, attrs={"allowGeometry": False}),
        )

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "This object type doesn't support geometry",
        )

    def test_create_object_with_geometry_without_allowGeometry(self, m):
        """test the support of Objecttypes api without allowGeometry property"""
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        object_type_response = mock_objecttype(self.object_type.url)
        del object_type_response["allowGeometry"]
        m.get(self.object_type.url, json=object_type_response)
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_object_with_empty_data_valid(self, m):
        """
        regression test for https://github.com/maykinmedia/objects-api/issues/371
        """
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        objecttype_version_response = mock_objecttype_version(self.object_type.url)
        objecttype_version_response["jsonSchema"]["required"] = []
        m.get(
            f"{self.object_type.url}/versions/1",
            json=objecttype_version_response,
        )
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_object_with_empty_data_invalid(self, m):
        """
        regression test for https://github.com/maykinmedia/objects-api/issues/371
        """
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

        error = get_validation_errors(response, "record.correctionFor")

        self.assertEqual(
            error["reason"],
            "Object with index=5 does not exist.",
        )

    def test_update_object_type_invalid(self, m):
        old_object_type = ObjectTypeFactory.create(service=self.object_type.service)
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
        obj = initial_record.object

        url = reverse("object-detail", args=[obj.uuid])
        data = {"type": self.object_type.url}

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        type_error = get_validation_errors(response, "type")

        self.assertEqual(type_error["reason"], "This field can't be changed")

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

        error = get_validation_errors(response, "uuid")

        self.assertEqual(
            error["reason"],
            "This field can't be changed",
        )

    def test_update_geometry_not_allowed(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(
            self.object_type.url,
            json=mock_objecttype(self.object_type.url, attrs={"allowGeometry": False}),
        )

        initial_record = ObjectRecordFactory.create(
            object__object_type=self.object_type, geometry=None
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            }
        }

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "nonFieldErrors")

        self.assertEqual(
            error["reason"],
            "This object type doesn't support geometry",
        )

    def test_create_object_with_duplicate_uuid_returns_400(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        url = reverse("object-list")

        data = {
            "uuid": "11111111-1111-1111-1111-111111111111",
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30},
                "startAt": "2026-02-05",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error = get_validation_errors(response, "uuid")

        self.assertEqual(error["reason"], "An object with this UUID already exists.")
        self.assertEqual(error["code"], "unique")
