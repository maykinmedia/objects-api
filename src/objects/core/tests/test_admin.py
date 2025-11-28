import re

from django.test import override_settings, tag
from django.urls import reverse

import requests_mock
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

            response = self.app.get(
                list_url, params={"q": "foo__icontains__bar"}, user=self.user
            )

            self.assertEqual(get_num_results(response), 1)

        with self.subTest("search is disabled if OBJECTS_ADMIN_SEARCH_DISABLED=True"):
            with override_settings(OBJECTS_ADMIN_SEARCH_DISABLED=True):
                response = self.app.get(
                    reverse("admin:core_object_changelist"), user=self.user
                )

                self.assertIsNone(response.html.find("input", {"id": "searchbar"}))

                response = self.app.get(list_url, params={"q": "bar"}, user=self.user)

                self.assertEqual(get_num_results(response), 2)

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

    @tag("gh-621")
    def test_object_admin_search_json_key_operator_value(self):
        object1 = ObjectFactory()
        ObjectRecordFactory(
            object=object1,
            data={"id_nummer": 1, "naam": "Boomgaard", "plantDate": "2025-01-01"},
        )
        object2 = ObjectFactory()
        ObjectRecordFactory(
            object=object2,
            data={"id_nummer": 2, "naam": "Appelboom", "plantDate": "2025-06-15"},
        )
        object3 = ObjectFactory()
        ObjectRecordFactory(
            object=object3,
            data={"id_nummer": 3, "naam": "Peren", "plantDate": "2025-12-31"},
        )
        object4 = ObjectFactory()
        ObjectRecordFactory(
            object=object4,
            data={
                "id_nummer": 4,
                "naam": "Kersen",
                "plantDate": "2025-07-20",
                "location": {"city": "Amsterdam", "region": "Noord-Holland"},
            },
        )

        list_url = reverse("admin:core_object_changelist")

        def get_row_pks(response):
            rows = response.html.select("#result_list tbody tr")
            pks = []
            for row in rows:
                href = row.select_one("th a")["href"]
                pks.append(int(re.search(r"\d+", href).group()))
            return pks

        with self.subTest("Exact match"):
            response = self.app.get(
                list_url, params={"q": "id_nummer__exact__1"}, user=self.user
            )
            self.assertEqual(get_row_pks(response), [object1.pk])

        with self.subTest("Nested JSON value match"):
            response = self.app.get(
                list_url,
                params={"q": "location__city__exact__Amsterdam"},
                user=self.user,
            )
            self.assertEqual(get_row_pks(response), [object4.pk])

        with self.subTest("Nested"):
            response = self.app.get(
                list_url,
                params={"q": "location__city__Amsterdam"},
                user=self.user,
            )
            self.assertEqual(get_row_pks(response), [object4.pk])

        with self.subTest("icontains"):
            response = self.app.get(
                list_url, params={"q": "naam__icontains__boom"}, user=self.user
            )
            self.assertCountEqual(get_row_pks(response), [object1.pk, object2.pk])

        with self.subTest("Default operator"):
            response = self.app.get(
                list_url, params={"q": "naam__Boomgaard"}, user=self.user
            )
            self.assertEqual(get_row_pks(response), [object1.pk])

        with self.subTest("Numeric comparison gt"):
            response = self.app.get(
                list_url, params={"q": "id_nummer__gt__1"}, user=self.user
            )
            self.assertCountEqual(
                get_row_pks(response), [object2.pk, object3.pk, object4.pk]
            )

        with self.subTest("Date exact"):
            response = self.app.get(
                list_url, params={"q": "plantDate__exact__2025-06-15"}, user=self.user
            )
            self.assertEqual(get_row_pks(response), [object2.pk])

        with self.subTest("Date gt"):
            response = self.app.get(
                list_url, params={"q": "plantDate__gt__2025-01-01"}, user=self.user
            )
            self.assertCountEqual(
                get_row_pks(response), [object2.pk, object3.pk, object4.pk]
            )

        with self.subTest("Date lt"):
            response = self.app.get(
                list_url, params={"q": "plantDate__lt__2025-12-01"}, user=self.user
            )
            self.assertCountEqual(
                get_row_pks(response), [object1.pk, object2.pk, object4.pk]
            )

        with self.subTest("Date comparison gte"):
            response = self.app.get(
                list_url, params={"q": "plantDate__gte__2025-06-15"}, user=self.user
            )
            self.assertCountEqual(
                get_row_pks(response), [object2.pk, object3.pk, object4.pk]
            )

        with self.subTest("Date comparison lte"):
            response = self.app.get(
                list_url, params={"q": "plantDate__lte__2025-06-15"}, user=self.user
            )
            self.assertCountEqual(get_row_pks(response), [object1.pk, object2.pk])
