from django.conf import settings

import requests
from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import SelfTestFailed
from zds_client.client import ClientError
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service


class ObjecttypesStep(BaseConfigurationStep):
    """
    Configure credentials for Objects API to request Objecttypes API

    Normal mode doesn't change the token after its initial creation.
    If the token is changed, run this command with 'overwrite' flag
    """

    verbose_name = "Objecttypes Configuration"
    required_settings = [
        "OBJECTTYPES_API_ROOT",
        "OBJECTS_OBJECTTYPES_TOKEN",
    ]
    enable_setting = "OBJECTS_OBJECTTYPES_CONFIG_ENABLE"

    def is_configured(self) -> bool:
        return Service.objects.filter(api_root=settings.OBJECTTYPES_API_ROOT).exists()

    def configure(self) -> None:
        service, created = Service.objects.update_or_create(
            api_root=settings.OBJECTTYPES_API_ROOT,
            defaults={
                "label": "Objecttypes API",
                "api_type": APITypes.orc,
                "oas": settings.OBJECTTYPES_API_OAS,
                "auth_type": AuthTypes.api_key,
                "header_key": "Authorization",
                "header_value": f"Token {settings.OBJECTS_OBJECTTYPES_TOKEN}",
            },
        )
        if not created:
            service.oas = settings.OBJECTTYPES_API_OAS
            service.header_value = f"Token {settings.OBJECTS_OBJECTTYPES_TOKEN}"
            service.save(update_fields=["oas", "header_value"])

    def test_configuration(self) -> None:
        """
        This check depends on the configuration in Objecttypes
        """
        client = Service.objects.get(
            api_root=settings.OBJECTTYPES_API_ROOT
        ).build_client()
        try:
            client.list("objecttype")
        except (requests.RequestException, ClientError) as exc:
            raise SelfTestFailed(
                "Could not Could not retrieve list of objecttypes from Objecttypes API."
            ) from exc
