import json
import uuid
from datetime import date, timedelta
from typing import cast

import requests_mock
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.models import Object, ObjectType
from objects.core.tests.factories import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from ..utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get
from .utils import reverse, reverse_lazy

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@freeze_time("2020-08-08")
@requests_mock.Mocker()
class ObjectApiTests(TokenAuthMixin, APITestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = cast(
            ObjectType, ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        )
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def test_list_actual_objects(self, m):
        object_record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type,
            start_at=date.today(),
        )
        ObjectRecordFactory.create(
            object__object_type=self.object_type,
            start_at=date.today() - timedelta(days=10),
            end_at=date.today() - timedelta(days=1),
        )
        url = reverse("object-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f'http://testserver{reverse("object-detail", args=[object_record1.object.uuid])}',
                        "uuid": str(object_record1.object.uuid),
                        "type": object_record1.object.object_type.url,
                        "record": {
                            "index": object_record1.index,
                            "typeVersion": object_record1.version,
                            "data": object_record1.data,
                            "geometry": json.loads(object_record1.geometry.json),
                            "startAt": object_record1.start_at.isoformat(),
                            "endAt": object_record1.end_at,
                            "registrationAt": object_record1.registration_at.isoformat(),
                            "correctionFor": None,
                            "correctedBy": None,
                        },
                    }
                ],
            },
        )

    def test_retrieve_object(self, m):
        object = ObjectFactory.create(object_type=self.object_type)
        object_record = ObjectRecordFactory.create(
            object=object,
            start_at=date.today(),
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
                "uuid": str(object.uuid),
                "type": object.object_type.url,
                "record": {
                    "index": object_record.index,
                    "typeVersion": object_record.version,
                    "data": object_record.data,
                    "geometry": json.loads(object_record.geometry.json),
                    "startAt": object_record.start_at.isoformat(),
                    "endAt": object_record.end_at,
                    "registrationAt": object_record.registration_at.isoformat(),
                    "correctionFor": None,
                    "correctedBy": None,
                },
            },
        )

    def test_retrieve_by_index(self, m):
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type,
            start_at=date(2020, 1, 1),
            geometry="POINT (4.910649523925713 52.37240093589432)",
            index=1,
        )

        object = record1.object

        record2 = ObjectRecordFactory.create(
            object=object, start_at=date.today(), correct=record1, index=2
        )

        with self.subTest(record=record1):
            url = reverse("object-history-detail", args=[object.uuid, 1])

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(
                data,
                {
                    "index": 1,
                    "typeVersion": record1.version,
                    "data": record1.data,
                    "geometry": json.loads(record1.geometry.json),
                    "startAt": record1.start_at.isoformat(),
                    "endAt": record2.start_at.isoformat(),
                    "registrationAt": record1.registration_at.isoformat(),
                    "correctionFor": None,
                    "correctedBy": 2,
                },
            )

        with self.subTest(record=record2):
            url = reverse("object-history-detail", args=[object.uuid, 2])

            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(
                data,
                {
                    "index": 2,
                    "typeVersion": record2.version,
                    "data": record2.data,
                    "geometry": json.loads(record2.geometry.json),
                    "startAt": record2.start_at.isoformat(),
                    "endAt": None,
                    "registrationAt": record2.registration_at.isoformat(),
                    "correctionFor": 1,
                    "correctedBy": None,
                },
            )

    def test_create_object(self, m):
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

        object = Object.objects.get()

        self.assertEqual(object.object_type, self.object_type)

        record = object.records.get()

        self.assertEqual(record.version, 1)
        self.assertEqual(record.data, {"plantDate": "2020-04-12", "diameter": 30})
        self.assertEqual(record.start_at, date(2020, 1, 1))
        self.assertEqual(record.registration_at, date(2020, 8, 8))
        self.assertEqual(record.geometry.coords, (4.910649523925713, 52.37240093589432))
        self.assertIsNone(record.end_at)

    def test_update_object(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        # other object - to check that correction works when there is another record with the same index
        ObjectRecordFactory.create(object__object_type=self.object_type)
        initial_record = ObjectRecordFactory.create(
            object__object_type=self.object_type
        )
        object = initial_record.object

        assert initial_record.end_at is None

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "type": object.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
                "correctionFor": initial_record.index,
            },
        }

        response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        object.refresh_from_db()
        initial_record.refresh_from_db()

        self.assertEqual(object.object_type, self.object_type)
        self.assertEqual(object.records.count(), 2)

        current_record = object.current_record

        self.assertEqual(current_record.version, 1)
        self.assertEqual(
            current_record.data, {"plantDate": "2020-04-12", "diameter": 30}
        )
        self.assertEqual(
            current_record.geometry.coords, (4.910649523925713, 52.37240093589432)
        )
        self.assertEqual(current_record.start_at, date(2020, 1, 1))
        self.assertEqual(current_record.registration_at, date(2020, 8, 8))
        self.assertIsNone(current_record.end_at)
        self.assertEqual(current_record.correct, initial_record)
        # assert changes to initial record
        self.assertNotEqual(current_record, initial_record)
        self.assertEqual(initial_record.corrected, current_record)
        self.assertEqual(initial_record.end_at, date(2020, 1, 1))

    def test_patch_object_record(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        initial_record = ObjectRecordFactory.create(
            version=1,
            object__object_type=self.object_type,
            start_at=date.today(),
            data={"name": "Name", "diameter": 20},
        )
        object = initial_record.object

        url = reverse("object-detail", args=[object.uuid])
        data = {
            "record": {
                "data": {"plantDate": "2020-04-12", "diameter": 30, "name": None},
                "startAt": "2020-01-01",
                "correctionFor": initial_record.index,
            },
        }

        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        initial_record.refresh_from_db()

        self.assertEqual(object.records.count(), 2)

        current_record = object.current_record

        self.assertEqual(current_record.version, initial_record.version)
        # The actual behavior of the data merging is in test_merge_patch.py:
        self.assertEqual(
            current_record.data,
            {"plantDate": "2020-04-12", "diameter": 30, "name": None},
        )
        self.assertEqual(current_record.start_at, date(2020, 1, 1))
        self.assertEqual(current_record.registration_at, date(2020, 8, 8))
        self.assertIsNone(current_record.end_at)
        self.assertEqual(current_record.correct, initial_record)
        # assert changes to initial record
        self.assertNotEqual(current_record, initial_record)
        self.assertEqual(initial_record.corrected, current_record)
        self.assertEqual(initial_record.end_at, date(2020, 1, 1))

    def test_delete_object(self, m):
        record = ObjectRecordFactory.create(object__object_type=self.object_type)
        object = record.object
        url = reverse("object-detail", args=[object.uuid])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Object.objects.count(), 0)

    def test_history_object(self, m):
        record1 = ObjectRecordFactory.create(
            object__object_type=self.object_type,
            start_at=date(2020, 1, 1),
            geometry="POINT (4.910649523925713 52.37240093589432)",
        )
        object = record1.object
        record2 = ObjectRecordFactory.create(
            object=object, start_at=date.today(), correct=record1
        )
        url = reverse("object-history", args=[object.uuid])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(
            data,
            {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "index": 1,
                        "typeVersion": record1.version,
                        "data": record1.data,
                        "geometry": json.loads(record1.geometry.json),
                        "startAt": record1.start_at.isoformat(),
                        "endAt": record2.start_at.isoformat(),
                        "registrationAt": record1.registration_at.isoformat(),
                        "correctionFor": None,
                        "correctedBy": 2,
                    },
                    {
                        "index": 2,
                        "typeVersion": record2.version,
                        "data": record2.data,
                        "geometry": json.loads(record2.geometry.json),
                        "startAt": record2.start_at.isoformat(),
                        "endAt": None,
                        "registrationAt": date.today().isoformat(),
                        "correctionFor": 1,
                        "correctedBy": None,
                    },
                ],
            },
        )

    # In the ticket https://github.com/maykinmedia/objects-api/issues/282 we discovered that updating an object \
    # where the startAt value has been modified with an earlier date causes an 500 response.
    def test_updating_object_after_changing_the_startAt_value_returns_200(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        object_uuid = uuid.uuid4()

        url_object_list = reverse("object-list")
        start_data = {
            "uuid": object_uuid,
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-02",
            },
        }

        response_object_list = self.client.post(
            url_object_list, start_data, **GEO_WRITE_KWARGS
        )

        self.assertEqual(response_object_list.status_code, status.HTTP_201_CREATED)

        url_object_update = reverse("object-detail", args=[object_uuid])
        modified_data = {
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

        response_object_details = self.client.put(
            url_object_update, modified_data, **GEO_WRITE_KWARGS
        )

        self.assertEqual(response_object_details.status_code, status.HTTP_200_OK)

        response_updating_data_after_startAt_modification = self.client.put(
            url_object_update, modified_data, **GEO_WRITE_KWARGS
        )

        self.assertEqual(
            response_updating_data_after_startAt_modification.status_code,
            status.HTTP_200_OK,
        )

    # regression test for https://github.com/maykinmedia/objects-api/issues/268
    def test_update_object_correctionFor(self, m):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        initial_record = ObjectRecordFactory.create(
            object__object_type=self.object_type, version=1
        )
        object = initial_record.object
        # correction record
        ObjectRecordFactory.create(object=object, version=1, correct=initial_record)

        url = reverse("object-detail", args=[object.uuid])
        modified_data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "startAt": "2024-01-01",
                "correctionFor": None,
            },
        }

        response = self.client.put(url, data=modified_data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, 200)

        object.refresh_from_db()
        self.assertEqual(object.records.count(), 3)

        last_record = object.last_record
        self.assertIsNone(last_record.correct)


@freeze_time("2024-08-31")
class ObjectsAvailableRecordsTests(TokenAuthMixin, APITestCase):
    """
    tests for https://github.com/maykinmedia/objects-api/issues/324

    today = 31.08

    Object X
      record 1: startAt=01.08 endAt=31.08 attr=A
      record 2: startAt=31.08 endAt=31.08 attr=B

    if filter records on attr=A, no record should be shown
    if no filter records on attr=A, record 2 should be shown
    """

    url = reverse_lazy("object-list")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

        cls.object = ObjectFactory.create(object_type=cls.object_type)
        ObjectRecordFactory.create(
            object=cls.object,
            data={"name": "old"},
            start_at="2024-08-01",
            end_at="2024-08-31",
            registration_at="2024-08-02",
        )
        ObjectRecordFactory.create(
            object=cls.object,
            data={"name": "new"},
            start_at="2024-08-31",
            end_at="2024-08-31",
            registration_at="2024-08-30",
        )

    @freeze_time("2024-08-31")
    def test_list_available_today(self):
        with self.subTest("filter on old name"):
            response = self.client.get(self.url, {"data_attrs": "name__exact__old"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 0)

        with self.subTest("without filter on old name"):
            response = self.client.get(self.url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 1)
            object_data = response.json()["results"][0]
            self.assertEqual(object_data["uuid"], str(self.object.uuid))
            self.assertEqual(object_data["record"]["data"], {"name": "new"})

    def test_list_available_for_date(self):
        with self.subTest("filter on old name"):
            response = self.client.get(
                self.url, {"data_attrs": "name__exact__old", "date": "2024-08-31"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 0)

        with self.subTest("filter on old name and old date"):
            response = self.client.get(
                self.url, {"data_attrs": "name__exact__old", "date": "2024-08-30"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 1)
            object_data = response.json()["results"][0]
            self.assertEqual(object_data["uuid"], str(self.object.uuid))
            self.assertEqual(object_data["record"]["data"], {"name": "old"})

        with self.subTest("without filter on old name"):
            response = self.client.get(self.url, {"date": "2024-08-31"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 1)
            object_data = response.json()["results"][0]
            self.assertEqual(object_data["uuid"], str(self.object.uuid))
            self.assertEqual(object_data["record"]["data"], {"name": "new"})

    def test_list_incorrect_date(self):
        response = self.client.get(self.url, {"date": "2024-31-08"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"date": ["Enter a valid date."]})

    def test_list_available_for_registration_date(self):
        with self.subTest("filter on old name"):
            response = self.client.get(
                self.url,
                {"data_attrs": "name__exact__old", "registrationDate": "2024-08-31"},
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 0)

        with self.subTest("filter on old name and old date"):
            response = self.client.get(self.url, {"registrationDate": "2024-08-29"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 1)
            object_data = response.json()["results"][0]
            self.assertEqual(object_data["uuid"], str(self.object.uuid))
            self.assertEqual(object_data["record"]["data"], {"name": "old"})

        with self.subTest("without filter on old name"):
            response = self.client.get(self.url, {"registrationDate": "2024-08-31"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["count"], 1)
            object_data = response.json()["results"][0]
            self.assertEqual(object_data["uuid"], str(self.object.uuid))
            self.assertEqual(object_data["record"]["data"], {"name": "new"})

    def test_list_incorrect_registration_date(self):
        response = self.client.get(self.url, {"registrationDate": "2024-31-08"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"registrationDate": ["Enter a valid date."]})
