from typing import cast

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.models import ObjectType
from objects.core.tests.factories import ObjectTypeFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import ClearCachesMixin, TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from ..utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get
from .utils import reverse

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@requests_mock.Mocker()
class JsonSchemaTests(TokenAuthMixin, ClearCachesMixin, APITestCase):
    """GH issue - https://github.com/maykinmedia/objects-api/issues/330"""

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

    def test_create_object_with_additional_properties_allowed(self, m):
        object_type_data = mock_objecttype_version(self.object_type.url)
        object_type_data["jsonSchema"]["additionalProperties"] = True

        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")

        m.get(f"{self.object_type.url}/versions/1", json=object_type_data)
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30, "newProperty": "some value"},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_object_with_additional_properties_not_allowed(self, m):
        object_type_data = mock_objecttype_version(self.object_type.url)
        object_type_data["jsonSchema"]["additionalProperties"] = False

        # mocks
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{self.object_type.url}/versions/1", json=object_type_data)
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30, "newProperty": "some value"},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(
            response, "Additional properties are not allowed", status_code=400
        )
