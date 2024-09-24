from django.test import TestCase, tag
from django.urls import reverse

from maykin_2fa.test import disable_admin_mfa
from vcr.unittest import VCRMixin
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

from objects.accounts.tests.factories import UserFactory
from objects.core.tests.factories import ObjectTypeFactory


@disable_admin_mfa()
class PermissionAdminTests(VCRMixin, TestCase):

    object_types_api = "http://127.0.0.1:8008/api/{version}/"

    def setUp(self):
        super().setUp()

        self.user = UserFactory(superuser=True)
        self.client.force_login(self.user)
        self.url = reverse("admin:token_permission_add")

    def _get_vcr(self, **kwargs):
        vcr = super()._get_vcr(**kwargs)
        vcr.filter_headers = ["authorization"]
        return vcr

    @tag("#449")
    def test_with_object_types_api_v1(self):
        """
        Regression test for #449.
        Test if Permission admin can still handle objecttypes API V1
        """

        v1_service = ServiceFactory(
            api_root=self.object_types_api.format(version="v1"),
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token 5cebbb33ffa725b6ed5e9e98300061218ba98d71",
        )
        ObjectTypeFactory(
            service=v1_service, uuid="71a2452a-66c3-4030-b5ec-a06035102e9e"
        )

        response = self.client.get(self.url)

        print(response)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.cassette.requests[1].uri,
            "http://127.0.0.1:8008/api/v1/objecttypes/71a2452a-66c3-4030-b5ec-a06035102e9e/versions",
        )

    @tag("#449")
    def test_with_object_types_api_v2(self):
        """
        Regression test for #449.
        Test if Permission admin can handle objecttypes API V2 which added pagination
        """
        v2_service = ServiceFactory(
            api_root=self.object_types_api.format(version="v2"),
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token 5cebbb33ffa725b6ed5e9e98300061218ba98d71",
        )
        ObjectTypeFactory(
            service=v2_service, uuid="71a2452a-66c3-4030-b5ec-a06035102e9e"
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.cassette.requests[1].uri,
            "http://127.0.0.1:8008/api/v2/objecttypes/71a2452a-66c3-4030-b5ec-a06035102e9e/versions",
        )
