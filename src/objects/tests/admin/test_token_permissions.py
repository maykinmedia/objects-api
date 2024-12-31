from django.urls import reverse_lazy

import requests_mock
from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa
from requests.exceptions import ConnectionError

from objects.accounts.tests.factories import UserFactory
from objects.token.constants import PermissionModes
from objects.token.tests.factories import (
    ObjectTypeFactory,
    PermissionFactory,
    TokenAuthFactory,
)

from ..utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@disable_admin_mfa()
@requests_mock.Mocker()
class AddPermissionTests(WebTest):
    url = reverse_lazy("admin:token_permission_add")

    def setUp(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.app.set_user(user)

    def test_add_permission_choices_without_properties(self, m):
        object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)
        TokenAuthFactory.create()

        # mock objecttypes api
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPES_API}objecttypes", json=[])
        m.get(object_type.url, json=mock_objecttype(object_type.url))
        version1 = mock_objecttype_version(object_type.url, attrs={"jsonSchema": {}})
        version2 = mock_objecttype_version(object_type.url, attrs={"version": 2})
        m.get(f"{object_type.url}/versions", json=[version1, version2])

        response = self.app.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["data_field_choices"], {})

    def test_get_permission_with_unavailable_objecttypes(self, m):
        """
        regression test for https://github.com/maykinmedia/objects-api/issues/373
        """
        object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)
        # mock objecttypes api
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPES_API}objecttypes", exc=ConnectionError)
        m.get(f"{object_type.url}/versions", exc=ConnectionError)

        response = self.app.get(self.url)

        self.assertEqual(response.status_code, 200)


@disable_admin_mfa()
@requests_mock.Mocker()
class ChangePermissionTests(WebTest):

    def setUp(self):
        user = UserFactory(is_superuser=True, is_staff=True)
        self.app.set_user(user)

        self.object_type = ObjectTypeFactory.create(service__api_root=OBJECT_TYPES_API)
        self.token_auth = TokenAuthFactory.create()

    def test_change_permission_data_field_choices_disabled(self, m):
        url = reverse_lazy("admin:token_permission_change")
        # use_fields disabled
        permission = PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
        )

        url = reverse_lazy("admin:token_permission_change", args=(permission.id,))

        # mock objecttypes api
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPES_API}objecttypes", json=[])
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))
        version1 = mock_objecttype_version(
            self.object_type.url, attrs={"jsonSchema": {}}
        )
        version2 = mock_objecttype_version(self.object_type.url, attrs={"version": 2})
        m.get(f"{self.object_type.url}/versions", json=[version1, version2])

        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["data_field_choices"], {})

    def test_change_permission_data_field_choices_enabled(self, m):
        url = reverse_lazy("admin:token_permission_change")
        # use_fields enabled
        permission = PermissionFactory.create(
            object_type=self.object_type,
            mode=PermissionModes.read_only,
            token_auth=self.token_auth,
            use_fields=True,
        )

        url = reverse_lazy("admin:token_permission_change", args=(permission.id,))

        # mock objecttypes api
        mock_service_oas_get(m, OBJECT_TYPES_API, "objecttypes")
        m.get(f"{OBJECT_TYPES_API}objecttypes", json=[])
        m.get(self.object_type.url, json=mock_objecttype(self.object_type.url))
        version1 = mock_objecttype_version(
            self.object_type.url, attrs={"jsonSchema": {}}
        )
        version2 = mock_objecttype_version(self.object_type.url, attrs={"version": 2})
        m.get(f"{self.object_type.url}/versions", json=[version1, version2])

        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["data_field_choices"],
            {
                self.object_type.id: {
                    1: {},
                    2: {
                        "diameter": "record__data__diameter",
                        "plantDate": "record__data__plantDate",
                    },
                }
            },
        )
