from unittest.mock import patch

from django.test import override_settings

from freezegun import freeze_time
from notifications_api_common.models import NotificationsConfig
from rest_framework import status
from rest_framework.test import APITestCase
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from objects.core.tests.factories import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
    ObjectTypeVersionFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from .utils import reverse


@freeze_time("2018-09-07T00:00:00Z")
@override_settings(NOTIFICATIONS_DISABLED=False)
class SendNotifTestCase(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory()
        ObjectTypeVersionFactory.create(object_type=cls.object_type)

        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def setUp(self):
        super().setUp()

        service, _ = Service.objects.update_or_create(
            api_root="https://notificaties-api.vng.cloud/api/v1/",
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

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_create_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        url = reverse("object-list")
        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()

        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "create",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
        )

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_update_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])

        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "update",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
        )

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_partial_update_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])

        data = {
            "type": f"https://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
            "record": {
                "typeVersion": 1,
                "data": {"plantDate": "2020-04-12", "diameter": 30},
                "geometry": {
                    "type": "Point",
                    "coordinates": [4.910649523925713, 52.37240093589432],
                },
                "startAt": "2020-01-01",
            },
        }

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "partial_update",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
        )

    @patch("notifications_api_common.viewsets.send_notification.delay")
    def test_send_notif_delete_object(self, mock_task):
        """
        Check if notifications will be send when Object is created
        """

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])
        full_url = f"http://testserver{url}"

        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.delete(url, **GEO_WRITE_KWARGS)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        mock_task.assert_called_once_with(
            {
                "kanaal": "objecten",
                "hoofdObject": full_url,
                "resource": "object",
                "resourceUrl": full_url,
                "actie": "destroy",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": f"http://testserver{reverse('objecttype-detail', args=[self.object_type.uuid])}",
                },
            },
        )
