from django.contrib.auth import get_user_model

import factory
from factory.django import DjangoModelFactory
from mozilla_django_oidc_db.constants import OIDC_ADMIN_CONFIG_IDENTIFIER
from mozilla_django_oidc_db.tests.factories import (
    OIDCClientFactory as BaseOIDCClientFactory,
    OIDCProviderFactory,
)

from objects.utils.tests.keycloak import KEYCLOAK_BASE_URL

User = get_user_model()


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = User

    class Params:
        superuser = factory.Trait(
            is_staff=True,
            is_superuser=True,
        )


class StaffUserFactory(UserFactory):
    is_staff = True


class OIDCClientFactory(BaseOIDCClientFactory):
    enabled = True

    class Params:  # pyright: ignore[reportIncompatibleVariableOverride]
        with_keycloak_provider = factory.Trait(
            oidc_provider=factory.SubFactory(
                OIDCProviderFactory,
                identifier="keycloak-provider",
                oidc_op_jwks_endpoint=f"{KEYCLOAK_BASE_URL}/certs",
                oidc_op_authorization_endpoint=f"{KEYCLOAK_BASE_URL}/auth",
                oidc_op_token_endpoint=f"{KEYCLOAK_BASE_URL}/token",
                oidc_op_user_endpoint=f"{KEYCLOAK_BASE_URL}/userinfo",
                oidc_op_logout_endpoint=f"{KEYCLOAK_BASE_URL}/logout",
            ),
            oidc_rp_client_id="testid",
            oidc_rp_client_secret="7DB3KUAAizYCcmZufpHRVOcD0TOkNO3I",
            oidc_rp_sign_algo="RS256",
        )
        with_admin = factory.Trait(
            identifier=OIDC_ADMIN_CONFIG_IDENTIFIER,
            oidc_rp_scopes_list=["email", "profile", "openid"],
        )
