from django.conf import settings
from django.urls import reverse

import requests
from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import SelfTestFailed

from objects.token.models import TokenAuth
from objects.utils import build_absolute_url


class DemoUserStep(BaseConfigurationStep):
    """
     Create demo user to request Objects API

    **NOTE** For now demo user has all permissions.
    """

    verbose_name = "Demo User Configuration"
    required_settings = [
        "DEMO_TOKEN",
        "DEMO_PERSON",
        "DEMO_EMAIL",
    ]
    enable_setting = "DEMO_CONFIG_ENABLE"

    def is_configured(self) -> bool:
        return TokenAuth.objects.filter(token=settings.DEMO_TOKEN).exists()

    def configure(self):
        token_auth, created = TokenAuth.objects.get_or_create(
            token=settings.DEMO_TOKEN,
            defaults={
                "contact_person": settings.DEMO_PERSON,
                "email": settings.DEMO_EMAIL,
                "is_superuser": True,
            },
        )
        if (
            token_auth.contact_person != settings.DEMO_PERSON
            or token_auth.email != settings.DEMO_EMAIL
        ):
            token_auth.contact_person = settings.DEMO_PERSON
            token_auth.email = settings.DEMO_EMAIL
            token_auth.save(update_fields=["contact_person", "email"])

    def test_configuration(self):
        endpoint = reverse("v2:object-list")
        full_url = build_absolute_url(endpoint, request=None)

        try:
            response = requests.get(
                full_url,
                headers={
                    "HTTP_AUTHORIZATION": f"Token {settings.OBJECTS_OBJECTTYPES_TOKEN}",
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SelfTestFailed(
                "Could not list objects for the configured token"
            ) from exc
