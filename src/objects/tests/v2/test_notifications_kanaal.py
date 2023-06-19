from io import StringIO
from unittest.mock import patch

from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import override_settings

from rest_framework.test import APITestCase
from notifications_api_common.kanalen import Kanaal
from notifications_api_common.models import NotificationsConfig

from zgw_consumers.models import Service

from objects.core.models import Object


@override_settings(IS_HTTPS=True)
class CreateNotifKanaalTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        site = Site.objects.get_current()
        site.domain = "example.com"
        site.save()

    @patch(
        "notifications_api_common.models.NotificationsConfig.get_client"
    )
    def test_kanaal_create_with_name(self, mock_get_client):
        """
        Test is request to create kanaal is send with specified kanaal name
        """
        client = mock_get_client.return_value
        client.list.return_value = []
        # ensure this is added to the registry
        Kanaal(label="kanaal_test", main_resource=Object)
        service = Service(api_root="https://example.com/api/v1")
        service.save()
        NotificationsConfig.notifications_api_service = service

        stdout = StringIO()
        call_command(
            "register_kanalen",
            kanalen=["kanaal_test"],
            stdout=stdout,
        )

        client.create.assert_called_once_with(
            "kanaal",
            {
                "naam": "kanaal_test",
                "documentatieLink": "https://example.com/ref/kanalen/#kanaal_test",
                "filters": [],
            },
        )

    @patch(
        "notifications_api_common.models.NotificationsConfig.get_client"
    )
    @override_settings(NOTIFICATIONS_KANAAL="dummy-kanaal")
    def test_kanaal_create_without_name(self, mock_get_client):
        """
        Test is request to create kanaal is send with default kanaal name
        """
        client = mock_get_client.return_value
        client.list.return_value = []
        client.create.reset_mock()
        # ensure this is added to the registry
        Kanaal(label="dummy-kanaal", main_resource=Object)
        service = Service(api_root="https://example.com/api/v1")
        service.save()
        NotificationsConfig.notifications_api_service = service

        stdout = StringIO()
        call_command(
            "register_kanalen",
            stdout=stdout,
        )

        client.create.assert_called_once_with(
            "kanaal",
            {
                "naam": "dummy-kanaal",
                "documentatieLink": "https://example.com/ref/kanalen/#dummy-kanaal",
                "filters": [],
            },
        )
