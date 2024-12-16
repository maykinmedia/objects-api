import logging
from typing import Any

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import (
    ConfigurationRunFailed,
    PrerequisiteFailed,
)

from objects.core.models import ObjectType
from objects.setup_configuration.models.token_auth import (
    TokenAuthGroupConfigurationModel,
)
from objects.token.models import Permission, TokenAuth

logger = logging.getLogger(__name__)


class TokenAuthConfigurationStep(
    BaseConfigurationStep[TokenAuthGroupConfigurationModel]
):
    """
    Configure tokens with permissions for other applications to access Objects API
    """

    namespace = "tokenauth"
    enable_setting = "tokenauth_config_enable"

    verbose_name = "Configuration to set up authentication tokens for objects"
    config_model = TokenAuthGroupConfigurationModel

    def _full_clean(self, instance: Any) -> None:
        try:
            instance.full_clean(exclude=("id",), validate_unique=False)
        except ValidationError as exception:
            raise ConfigurationRunFailed(
                ("Validation error(s) during instance cleaning: %s" % type(instance))
            ) from exception

    def _configure_permissions(self, token: TokenAuth, permissions: list) -> None:
        if len(permissions) == 0:
            logger.warning("No permissions provided for %s", token.identifier)

        for permission in permissions:
            try:
                permission_kwargs = {
                    "token_auth": token,
                    "object_type": ObjectType.objects.get(uuid=permission.object_type),
                    "mode": permission.mode,
                    "use_fields": permission.use_fields,
                    "fields": permission.fields,
                }
            except ObjectDoesNotExist as exception:
                raise PrerequisiteFailed(step=self, validation_error=exception)

            permission_instance = Permission(**permission_kwargs)
            self._full_clean(permission_instance)

            try:
                Permission.objects.update_or_create(
                    token_auth=permission_kwargs["token_auth"],
                    object_type=permission_kwargs["object_type"],
                    defaults={
                        "mode": permission_kwargs["mode"],
                        "use_fields": permission_kwargs["use_fields"],
                        "fields": permission_kwargs["fields"],
                    },
                )
            except IntegrityError as exception:
                raise ConfigurationRunFailed(
                    ("Failed configuring permission for token %s" % token.identifier)
                ) from exception

    def execute(self, model: TokenAuthGroupConfigurationModel) -> None:
        if len(model.items) == 0:
            logger.warning("No tokens provided for configuration")

        for item in model.items:
            logger.info("Configuring %s", item.identifier)

            token_kwargs = {
                "identifier": item.identifier,
                "token": item.token,
                "contact_person": item.contact_person,
                "email": item.email,
                "organization": item.organization,
                "application": item.application,
                "administration": item.administration,
                "is_superuser": item.is_superuser,
            }

            token_instance = TokenAuth(**token_kwargs)
            self._full_clean(token_instance)
            try:
                logger.debug("Saving %s", item.identifier)
                token, _ = TokenAuth.objects.update_or_create(
                    identifier=item.identifier,
                    defaults={
                        key: value
                        for key, value in token_kwargs.items()
                        if key != "identifier"
                    },
                )

                self._configure_permissions(token, item.permissions)

            except IntegrityError as exception:
                raise ConfigurationRunFailed(
                    "Failed configuring token %s" % item.identifier
                ) from exception

            logger.info("Configured %s", item.identifier)
