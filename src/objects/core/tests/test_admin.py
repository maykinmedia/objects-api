from django.test import override_settings, tag
from django.urls import reverse

from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

from objects.accounts.tests.factories import UserFactory
from objects.core.tests.factories import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)


@disable_admin_mfa()
class ObjectAdminTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory(superuser=True)

    @tag("gh-615")
    def test_object_changelist_filter_by_objecttype(self):
        service = ServiceFactory(
            api_root="http://objecttypes.local/api/v1/",
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token 5cebbb33ffa725b6ed5e9e98300061218ba98d71",
        )
        object_type = ObjectTypeFactory(
            service=service, uuid="71a2452a-66c3-4030-b5ec-a06035102e9e"
        )
        # Create 100 unused ObjectTypes, which creates 100 Services as well
        ObjectTypeFactory.create_batch(100)
        object1 = ObjectFactory(object_type=object_type)
        object2 = ObjectFactory()

        # Verify that the number of queries doesn't scale with the number of objecttypes
        with self.assertNumQueries(22):
            response = self.app.get(
                reverse("admin:core_object_changelist"),
                {"object_type__id__exact": object_type.pk},
                user=self.user,
            )

        self.assertEqual(response.status_code, 200)

        result_list = response.html.find("table", {"id": "result_list"})
        rows = result_list.find("tbody").find_all("tr")

        self.assertEqual(len(rows), 1)
        self.assertIn(str(object1.uuid), response.text)
        self.assertNotIn(str(object2.uuid), response.text)

    @tag("gh-621")
    def test_object_admin_search_disabled(self):
        list_url = reverse("admin:core_object_changelist")

        ObjectRecordFactory.create(data={"foo": "bar"})
        ObjectRecordFactory.create(data={"foo": "baz"})

        def get_num_results(response) -> int:
            result_list = response.html.find("table", {"id": "result_list"})
            return len(result_list.find("tbody").find_all("tr"))

        with self.subTest("search is enabled by default"):
            response = self.app.get(list_url, user=self.user)

            self.assertIsNotNone(response.html.find("input", {"id": "searchbar"}))

            response = self.app.get(list_url, params={"q": "bar"}, user=self.user)

            self.assertEqual(get_num_results(response), 1)

        with self.subTest("search is disabled if OBJECTS_ADMIN_SEARCH_DISABLED=True"):
            with override_settings(OBJECTS_ADMIN_SEARCH_DISABLED=True):
                response = self.app.get(
                    reverse("admin:core_object_changelist"), user=self.user
                )

                self.assertIsNone(response.html.find("input", {"id": "searchbar"}))

                response = self.app.get(list_url, params={"q": "bar"}, user=self.user)

                self.assertEqual(get_num_results(response), 2)
