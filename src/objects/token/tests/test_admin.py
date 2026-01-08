from django.test import TestCase, tag
from django.urls import reverse

from maykin_2fa.test import disable_admin_mfa
from maykin_common.vcr import VCRMixin
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

from objects.accounts.tests.factories import UserFactory
from objects.core.tests.factories import ObjectTypeFactory


@disable_admin_mfa()
class PermissionAdminTests(VCRMixin, TestCase):
    object_types_api = "http://127.0.0.1:8008/api/{version}/"

    def setUp(self):
        super().setUp()

        self.user = UserFactory.create(superuser=True)
        self.client.force_login(self.user)
        self.url = reverse("admin:token_permission_add")

    @tag("#449")
    def test_with_object_types_api_v2(self):
        """
        Regression test for #449.
        Test if Permission admin can handle objecttypes API V2 which added pagination
        """
        v2_service = ServiceFactory.create(
            api_root=self.object_types_api.format(version="v2"),
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token 5cebbb33ffa725b6ed5e9e98300061218ba98d71",
        )
        object_type = ObjectTypeFactory.create(
            service=v2_service, uuid="71a2452a-66c3-4030-b5ec-a06035102e9e"
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        form = response.context["adminform"].form
        choices = list(form.fields["object_type"].choices)

        self.assertEqual(
            choices[1][0].value,
            object_type.id,
        )
        self.assertEqual(
            choices[1][1],
            f"{v2_service.label}: {object_type._name}",
        )
