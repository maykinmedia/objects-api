from unittest.mock import MagicMock, patch

import requests_mock
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from objects.api.metrics import (
    objects_create_counter,
    objects_delete_counter,
    objects_update_counter,
    objecttype_create_counter,
    objecttype_delete_counter,
    objecttype_update_counter,
)
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
from .utils import reverse

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@freeze_time("2024-08-31")
class ObjectMetricsTests(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def create_object_with_record(self, diameter: int = 10):
        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(
            object=obj,
            version=1,
            data={"diameter": diameter},
            start_at="2024-08-31",
        )
        return obj

    @requests_mock.Mocker()
    @patch.object(objects_create_counter, "add", wraps=objects_create_counter.add)
    def test_objects_create_counter(self, m, mock_add: MagicMock):
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
                "data": {"diameter": 10},
                "startAt": "2024-08-31",
            },
        }
        response = self.client.post(url, data, **GEO_WRITE_KWARGS)
        self.assertEqual(response.status_code, 201)
        mock_add.assert_called_once_with(1)

    @requests_mock.Mocker()
    @patch.object(objects_update_counter, "add", wraps=objects_update_counter.add)
    def test_objects_update_counter(self, m, mock_add: MagicMock):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        obj = self.create_object_with_record()
        url = reverse("object-detail", args=[obj.uuid])
        data = {
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 20},
                "startAt": "2024-08-31",
            }
        }
        response = self.client.patch(url, data, **GEO_WRITE_KWARGS)
        self.assertEqual(response.status_code, 200)
        mock_add.assert_called_once_with(1)

    @requests_mock.Mocker()
    @patch.object(objects_delete_counter, "add", wraps=objects_delete_counter.add)
    def test_objects_delete_counter(self, m, mock_add: MagicMock):
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        obj = self.create_object_with_record()
        url = reverse("object-detail", args=[obj.uuid])
        response = self.client.delete(url, **GEO_WRITE_KWARGS)
        self.assertEqual(response.status_code, 204)

        mock_add.assert_called_once_with(1)


@freeze_time("2020-01-01")
class ObjectTypeMetricTests(TokenAuthMixin, APITestCase):
    @patch.object(objecttype_create_counter, "add", wraps=objecttype_create_counter.add)
    def test_objecttype_create_counter(self, mock_add: MagicMock):
        url = reverse("objecttype-list")

        response = self.client.post(
            url,
            {
                "name": "Boom",
                "namePlural": "Bomen",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        mock_add.assert_called_once_with(1)

    @patch.object(objecttype_update_counter, "add", wraps=objecttype_update_counter.add)
    def test_objecttype_update_counter(self, mock_add: MagicMock):
        obj = ObjectTypeFactory.create()
        url = reverse("objecttype-detail", args=[obj.uuid])

        response = self.client.patch(url, {"name": "test"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        mock_add.assert_called_once_with(1)

    @patch.object(objecttype_delete_counter, "add", wraps=objecttype_delete_counter.add)
    def test_objecttype_delete_counter(self, mock_add: MagicMock):
        obj = ObjectTypeFactory.create()
        url = reverse("objecttype-detail", args=[obj.uuid])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        mock_add.assert_called_once_with(1)
