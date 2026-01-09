import requests_mock
from rest_framework.test import APITestCase

from objects.core.models import ObjectType
from objects.core.tests.factories import ObjectTypeFactory
from objects.tests.utils import (
    mock_objecttype,
    mock_objecttype_version,
    mock_service_oas_get,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.client import get_objecttypes_client

from ..test import TokenAuthMixin

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@requests_mock.Mocker()
class ObjecttypesClientTest(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def test_list_objecttypes(self, m):
        object_type = ObjectType.objects.first()
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        object_type_mock = mock_objecttype(object_type.url)
        m.get(
            f"{OBJECT_TYPES_API}objecttypes",
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [object_type_mock],
            },
        )
        with get_objecttypes_client(object_type.service) as client:
            self.assertTrue(client.can_connect)
            data = client.list_objecttypes()
        self.assertEqual(data, [object_type_mock])
        self.assertEqual(len(data), 1)

    def test_get_objecttype(self, m):
        object_type = ObjectType.objects.first()
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(object_type.url, json=mock_objecttype(object_type.url))

        with get_objecttypes_client(object_type.service) as client:
            data = client.get_objecttype(object_type.uuid)
        self.assertTrue(data["url"], str(object_type.url))

    def test_list_objecttype_versions(self, m):
        object_type = ObjectType.objects.first()
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        object_type_mock = mock_objecttype(object_type.url)
        m.get(
            f"{OBJECT_TYPES_API}objecttypes",
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [object_type_mock],
            },
        )
        version_mock = mock_objecttype_version(object_type.url)
        m.get(
            f"{object_type.url}/versions",
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [version_mock],
            },
        )

        with get_objecttypes_client(object_type.service) as client:
            self.assertTrue(client.can_connect)
            data = client.list_objecttypes()
            self.assertEqual(data, [object_type_mock])
            self.assertEqual(len(data), 1)
            data = client.list_objecttype_versions(object_type.uuid)
            self.assertEqual(data, [version_mock])
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["version"], 1)

    def test_get_objecttype_version(self, m):
        object_type = ObjectType.objects.first()
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        with get_objecttypes_client(object_type.service) as client:
            data = client.get_objecttype_version(object_type.uuid, 1)
        self.assertEqual(data["url"], f"{self.object_type.url}/versions/1")
