from unittest import skip

from django.urls import reverse

import requests_mock
from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa
from requests.exceptions import HTTPError

from objects.accounts.tests.factories import UserFactory
from objects.token.tests.factories import ObjectTypeFactory

from ..utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get


@disable_admin_mfa()
@requests_mock.Mocker()
@skip("outdated")  # TODO view was removed
class ObjectTypeAdminVersionsTests(WebTest):
    def test_valid_response_view(self, m):
        objecttypes_api = "https://example.com/objecttypes/v1/"
        object_type = ObjectTypeFactory.create(service__api_root=objecttypes_api)
        mock_service_oas_get(m, objecttypes_api, "objecttypes")
        m.get(f"{objecttypes_api}objecttypes", json=[])
        m.get(object_type.url, json=mock_objecttype(object_type.url))
        version = mock_objecttype_version(object_type.url, attrs={"jsonSchema": {}})
        m.get(
            object_type.versions_url,
            json={
                "count": 1,
                "next": None,
                "previous": None,
                "results": [version],
            },
        )

        user = UserFactory.create(is_staff=True, is_superuser=True)

        # object_type exist
        url = reverse("admin:objecttype_versions", args=[object_type.pk])
        response = self.app.get(url, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

        # object_type does not exist
        url = reverse("admin:objecttype_versions", args=[object_type.pk + 1])
        response = self.app.get(url, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_endpoint_unreachable(self, m):
        user = UserFactory.create(is_staff=True, is_superuser=True)
        object_type = ObjectTypeFactory.create()
        m.get(object_type.versions_url, exc=HTTPError)

        url = reverse("admin:objecttype_versions", args=[object_type.pk])
        response = self.app.get(url, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_invalid_authentication_view(self, m):
        url = reverse("admin:objecttype_versions", args=[1])
        response = self.client.get(url)
        redirect_url = f"{reverse('admin:login')}?next={url}"
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_invalid_permission_view(self, m):
        user = UserFactory.create(is_staff=False, is_superuser=False)
        url = reverse("admin:objecttype_versions", args=[1])
        response = self.app.get(url, user=user, auto_follow=True)
        self.assertContains(
            response,
            f"You are authenticated as {user.username}, but are not authorized to access this page",
        )
