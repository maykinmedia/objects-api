from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import ConfigurationRunFailed

from objects.core.models import ObjectType
from objects.setup_configuration.models.objecttypes import ObjectTypesConfigurationModel


class ObjectTypesConfigurationStep(BaseConfigurationStep):
    """
    Configure references to objecttypes in the Objecttypes API.

    .. note:: Note that these objecttypes references should match instances in the Objecttypes API. Currently
            there is no configuration step to do this automatically, so these have to be configured
            manually or by loading fixtures.
    """

    config_model = ObjectTypesConfigurationModel
    verbose_name = "Objecttypes Configuration"

    namespace = "objecttypes"
    enable_setting = "objecttypes_config_enable"

    def execute(self, model: ObjectTypesConfigurationModel) -> None:
        for item in model.items:
            objecttype_kwargs = dict(
                uuid=item.uuid,
                name=item.name,
                name_plural=f"{item.name}s",
            )

            objecttype_instance = ObjectType(**objecttype_kwargs)

            try:
                objecttype_instance.full_clean(exclude=("id"), validate_unique=False)
            except ValidationError as exception:
                exception_message = (
                    f"Validation error(s) occured for objecttype {item.uuid}."
                )
                raise ConfigurationRunFailed(exception_message) from exception

            try:
                ObjectType.objects.update_or_create(
                    uuid=item.uuid,
                    defaults={
                        key: value
                        for key, value in objecttype_kwargs.items()
                        if key != "uuid"
                    },
                )
            except IntegrityError as exception:
                exception_message = f"Failed configuring ObjectType {item.uuid}."
                raise ConfigurationRunFailed(exception_message) from exception
