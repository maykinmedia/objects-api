from django.urls import reverse

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from objects.accounts.tests.factories import UserFactory


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
        self.assertEqual(response.json, [])
