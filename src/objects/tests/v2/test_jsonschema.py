from rest_framework import status
from rest_framework.test import APITestCase

from objects.core.tests.factories import ObjectTypeFactory, ObjectTypeVersionFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import ClearCachesMixin, TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from .utils import reverse


class JsonSchemaTests(TokenAuthMixin, ClearCachesMixin, APITestCase):
    """GH issue - https://github.com/maykinmedia/objects-api/issues/330"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory.create()
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def test_create_object_with_additional_properties_allowed(self):
        object_type_data = ObjectTypeVersionFactory.create(object_type=self.object_type)
        object_type_data.json_schema["additionalProperties"] = True
        object_type_data.save()

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"diameter": 30, "newProperty": "some value"},
                "startAt": "2020-01-01",
            },
        }

        response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_object_with_additional_properties_not_allowed(self):
        object_type_data = ObjectTypeVersionFactory.create(object_type=self.object_type)
        object_type_data.json_schema["additionalProperties"] = False
        object_type_data.save()

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
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
