from io import StringIO

from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import override_settings

import requests_mock
from notifications_api_common.kanalen import KANAAL_REGISTRY
from notifications_api_common.models import NotificationsConfig
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from objects.api.kanalen import ObjectKanaal
from objects.core.models import Object

NOTIFICATIONS_API_ROOT = "https://notificaties-api.vng.cloud/api/v1/"


@override_settings(IS_HTTPS=True)
class CreateNotifKanaalTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get_current()
        site.domain = "example.com"
        site.save()

        kanaal = ObjectKanaal(label="kanaal_test", main_resource=Object)
        cls.addClassCleanup(lambda: KANAAL_REGISTRY.remove(kanaal))

        service, _ = Service.objects.update_or_create(
            api_root=NOTIFICATIONS_API_ROOT,
            defaults=dict(
                api_type=APITypes.nrc,
                client_id="test",
                secret="test",
                user_id="test",
                user_representation="Test",
            ),
        )
        config = NotificationsConfig.get_solo()
        config.notifications_api_service = service
        config.save()

    @requests_mock.Mocker()
    def test_kanaal_create_with_name(self, m):
        """
        Test is request to create kanaal is send with specified kanaal name
        """
        m.get(f"{NOTIFICATIONS_API_ROOT}kanaal?naam=kanaal_test", json=[])
        m.post(f"{NOTIFICATIONS_API_ROOT}kanaal")

        stdout = StringIO()
        call_command(
            "register_kanalen",
            kanalen=["kanaal_test"],
            stdout=stdout,
        )

        self.assertEqual(m.last_request.url, f"{NOTIFICATIONS_API_ROOT}kanaal")
        self.assertEqual(m.last_request.method, "POST")
        self.assertEqual(
            m.last_request.json(),
            {
                "naam": "kanaal_test",
                "documentatieLink": "https://example.com/ref/kanalen/#kanaal_test",
                "filters": [],
            },
        )

    @override_settings(NOTIFICATIONS_KANAAL="dummy-kanaal")
    @requests_mock.Mocker()
    def test_kanaal_create_without_name(self, m):
        """
        Test is request to create kanaal is send with default kanaal name
        """
        m.get(f"{NOTIFICATIONS_API_ROOT}kanaal", json=[])
        m.post(f"{NOTIFICATIONS_API_ROOT}kanaal")

        stdout = StringIO()
        call_command(
            "register_kanalen",
            stdout=stdout,
        )

        post_req1, post_req2 = [
            req
            for req in m.request_history
            if req.method == "POST" and req.url == f"{NOTIFICATIONS_API_ROOT}kanaal"
        ]
        self.assertEqual(
            post_req1.json(),
            {
                "naam": "kanaal_test",
                "documentatieLink": "https://example.com/ref/kanalen/#kanaal_test",
                "filters": [],
            },
        )
        self.assertEqual(
            post_req2.json(),
            {
                "naam": "objecten",
                "documentatieLink": "https://example.com/ref/kanalen/#objecten",
                "filters": ["object_type"],
            },
        )
