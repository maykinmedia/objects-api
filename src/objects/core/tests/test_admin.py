from django.test import tag
from django.urls import reverse

import requests_mock
from django_webtest import WebTest
from maykin_2fa.test import disable_admin_mfa
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

from objects.accounts.tests.factories import UserFactory
from objects.core.tests.factories import ObjectFactory, ObjectTypeFactory
from objects.tests.utils import mock_objecttype_version


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

    @tag("gh-677")
    def test_add_new_objectrecord(self):
        service = ServiceFactory(
            api_root="http://objecttypes.local/api/v1/",
            auth_type=AuthTypes.api_key,
            header_key="Authorization",
            header_value="Token 5cebbb33ffa725b6ed5e9e98300061218ba98d71",
        )
        object_type = ObjectTypeFactory(
            service=service, uuid="71a2452a-66c3-4030-b5ec-a06035102e9e"
        )
        object_type_url = (
            "http://objecttypes.local/api/v1/"
            "objecttypes/71a2452a-66c3-4030-b5ec-a06035102e9e/versions/1"
        )
        object = ObjectFactory(object_type=object_type)

        self.assertEqual(object.records.count(), 0)

        # Verify that the number of queries doesn't scale with the number of objecttypes
        # with self.assertNumQueries(22):
        response = self.app.get(
            reverse("admin:core_object_change", kwargs={"object_id": object.pk}),
            user=self.user,
        )

        self.assertEqual(response.status_code, 200)

        form = response.forms["object_form"]
        form["records-0-data"] = '{"diameter": 4, "plantDate": "2025-01-01"}'
        form["records-0-version"] = 1
        form["records-0-start_at"] = "2025-01-01"

        with requests_mock.Mocker() as m:
            m.get(object_type_url, json=mock_objecttype_version(object_type_url))
            response = form.submit()

        self.assertEqual(object.records.count(), 1)
