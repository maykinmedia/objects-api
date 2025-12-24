import json

from django.urls import reverse_lazy

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa

from objects.accounts.tests.factories import UserFactory
from objects.token.tests.factories import ObjectTypeFactory, TokenAuthFactory

from ...core.tests.factories import ObjectTypeVersionFactory


@disable_admin_mfa()
class AddPermissionTests(WebTest):
    url = reverse_lazy("admin:token_permission_add")

    def setUp(self):
        user = UserFactory.create(is_superuser=True, is_staff=True)
        self.app.set_user(user)

    def test_add_permission_choices_without_properties(self):
        object_type = ObjectTypeFactory.create()
        TokenAuthFactory.create()

        version1 = ObjectTypeVersionFactory.create(
            object_type=object_type, json_schema={}
        )
        version2 = ObjectTypeVersionFactory.create(object_type=object_type, version=2)

        response = self.app.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(version1.json_schema, {})
        self.assertTrue("diameter", version2.json_schema["properties"].keys())
        self.assertTrue("plantDate", version2.json_schema["properties"].keys())

        self.assertFalse("record__data__diameter" in str(response.content))
        self.assertFalse("record__data__plantDate" in str(response.content))

    def test_token_auth_is_preselected_in_select(self):
        token = TokenAuthFactory.create()
        url = f"{self.url}?token_auth={token.pk}"
        page = self.app.get(url)

        form_data_script = page.html.find("script", {"id": "form-data"})

        self.assertIsNotNone(form_data_script)

        form_data = json.loads(form_data_script.string)

        token_auth_value = form_data["values"].get("token_auth")

        self.assertEqual(token_auth_value, str(token.pk))
