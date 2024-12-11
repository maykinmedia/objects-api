from django.db import IntegrityError

from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import ConfigurationRunFailed
from zgw_consumers.contrib.setup_configuration.models import (
    SingleServiceConfigurationModel,
)
from zgw_consumers.models import Service


class ObjectTypesConnectionConfigurationStep(
    BaseConfigurationStep[SingleServiceConfigurationModel]
):
    config_model = SingleServiceConfigurationModel
    verbose_name = "Objecttypes connection configuration"

    namespace = "objecttypes_connection"
    enable_setting = "objecttypes_connection_config_enable"

    def execute(self, model: SingleServiceConfigurationModel) -> None:
        service_kwargs = dict(
            slug=model.identifier,
            label=model.label,
            api_type=model.api_type,
            api_root=model.api_root,
            api_connection_check_path=model.api_connection_check_path,
            auth_type=model.auth_type,
            client_id=model.client_id,
            secret=model.secret,
            header_key=model.header_key,
            header_value=model.header_value,
            nlx=model.nlx,
            user_id=model.user_id,
            user_representation=model.user_representation,
            timeout=model.timeout,
        )

        service = Service(**service_kwargs)

        try:
            Service.objects.update_or_create(
                slug=service.slug,
                defaults={
                    key: value for key, value in service_kwargs.items() if key != "slug"
                },
            )
        except IntegrityError as exception:
            exception_message = (
                f"Failed configuring ObjectType connection {service.slug}."
            )
            raise ConfigurationRunFailed(exception_message) from exception
