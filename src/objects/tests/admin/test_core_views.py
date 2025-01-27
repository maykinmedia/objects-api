from django.urls import reverse_lazy

from django_webtest import WebTest
import requests_mock
from django.test import TestCase, override_settings
from maykin_2fa.test import disable_admin_mfa
from requests.exceptions import ConnectionError

from objects.accounts.tests.factories import UserFactory
from objects.token.tests.factories import ObjectTypeFactory, TokenAuthFactory
from django.urls import reverse
from ..utils import mock_objecttype, mock_objecttype_version, mock_service_oas_get


@disable_admin_mfa()
class ObjectTypeAdminVersionsTests(WebTest):

    def test_authentication_view(self):
        url = reverse("admin:objecttype_versions", args=[1])
        response = self.client.get(url)
        redirect_url = f"{reverse('admin:login')}?next={url}"
        self.assertRedirects(response, redirect_url, status_code=302)

    def test_permission_view(self):
        user = UserFactory.create(is_staff=False, is_superuser=False)
        url = reverse("admin:objecttype_versions", args=[1])
        response = self.app.get(url, user=user, auto_follow=True)
        self.assertContains(
            response,
            f"You are authenticated as {user.username}, but are not authorized to access this page",
        )

        user.is_staff = True
        user.save()

        url = reverse("admin:objecttype_versions", args=[1])
        response = self.app.get(url, user=user)
        self.assertEqual(
            response.json,
            {
                "count": 0,
                "next": None,
                "previous": None,
                "results": [],
            },
        )
