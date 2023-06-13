from unittest.mock import patch

from django.test import override_settings

import requests_mock
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from vng_api_common.notifications.models import NotificationsConfig
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

from objects.core.tests.factories import (
    ObjectFactory,
    ObjectRecordFactory,
    ObjectTypeFactory,
)
from objects.token.constants import PermissionModes
from objects.token.tests.factories import PermissionFactory
from objects.utils.test import TokenAuthMixin

from ..constants import GEO_WRITE_KWARGS
from ..utils import (
    mock_objecttype,
    mock_objecttype_version,
    mock_service_oas_get,
    notifications_client_mock,
)
from .utils import reverse

OBJECT_TYPES_API = "https://example.com/objecttypes/v1/"


@freeze_time("2018-09-07T00:00:00Z")
@override_settings(NOTIFICATIONS_DISABLED=False)
@requests_mock.Mocker()
class SendNotifTestCase(TokenAuthMixin, APITestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.object_type = ObjectTypeFactory(service__api_root=OBJECT_TYPES_API)
        PermissionFactory.create(
            object_type=cls.object_type,
            mode=PermissionModes.read_and_write,
            token_auth=cls.token_auth,
        )

    def setUp(self):
        super().setUp()

        config = NotificationsConfig.get_solo()
        Service.objects.update_or_create(
            api_root=config.api_root,
            defaults=dict(
                api_type=APITypes.nrc,
                client_id="test",
                secret="test",
                user_id="test",
                user_representation="Test",
            ),
        )

    @patch("zds_client.Client.from_url", side_effect=notifications_client_mock)
    def test_send_notif_create_object(self, mocker, mock_client):
        """
        Check if notifications will be send when Object is created
        """
        client = mock_client.return_value
        mock_service_oas_get(mocker, OBJECT_TYPES_API, "objecttypes")
        mocker.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        mocker.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        url = reverse("object-list")
        data = {
            "type": self.object_type.url,
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

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.post(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        data = response.json()

        client.create.assert_called_once_with(
            "notificaties",
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "create",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": self.object_type.url,
                },
            },
        )

    @patch("zds_client.Client.from_url", side_effect=notifications_client_mock)
    def test_send_notif_update_object(self, mocker, mock_client):
        """
        Check if notifications will be send when Object is created
        """
        client = mock_client.return_value
        mock_service_oas_get(mocker, OBJECT_TYPES_API, "objecttypes")
        mocker.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        mocker.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])

        data = {
            "type": self.object_type.url,
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

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.put(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        client.create.assert_called_once_with(
            "notificaties",
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "update",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": self.object_type.url,
                },
            },
        )

    @patch("zds_client.Client.from_url", side_effect=notifications_client_mock)
    def test_send_notif_partial_update_object(self, mocker, mock_client):
        """
        Check if notifications will be send when Object is created
        """
        client = mock_client.return_value
        mock_service_oas_get(mocker, OBJECT_TYPES_API, "objecttypes")
        mocker.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )
        mocker.get(self.object_type.url, json=mock_objecttype(self.object_type.url))

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])

        data = {
            "type": self.object_type.url,
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

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.patch(url, data, **GEO_WRITE_KWARGS)

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        data = response.json()

        client.create.assert_called_once_with(
            "notificaties",
            {
                "kanaal": "objecten",
                "hoofdObject": data["url"],
                "resource": "object",
                "resourceUrl": data["url"],
                "actie": "partial_update",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": self.object_type.url,
                },
            },
        )

    @patch("zds_client.Client.from_url", side_effect=notifications_client_mock)
    def test_send_notif_delete_object(self, mocker, mock_client):
        """
        Check if notifications will be send when Object is created
        """
        client = mock_client.return_value
        mock_service_oas_get(mocker, OBJECT_TYPES_API, "objecttypes")
        mocker.get(
            f"{self.object_type.url}/versions/1",
            json=mock_objecttype_version(self.object_type.url),
        )

        obj = ObjectFactory.create(object_type=self.object_type)
        ObjectRecordFactory.create(object=obj)
        url = reverse("object-detail", args=[obj.uuid])
        full_url = f"http://testserver{url}"

        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self.client.delete(url, **GEO_WRITE_KWARGS)

        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, response.data
        )

        client.create.assert_called_once_with(
            "notificaties",
            {
                "kanaal": "objecten",
                "hoofdObject": full_url,
                "resource": "object",
                "resourceUrl": full_url,
                "actie": "destroy",
                "aanmaakdatum": "2018-09-07T02:00:00+02:00",
                "kenmerken": {
                    "objectType": self.object_type.url,
                },
            },
        )
