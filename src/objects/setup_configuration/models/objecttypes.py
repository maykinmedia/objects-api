from django_setup_configuration.fields import DjangoModelRef
from django_setup_configuration.models import ConfigurationModel
from zgw_consumers.models import Service
from pydantic import Field

from objects.core.models import ObjectType


class ObjectTypeConfigurationModel(ConfigurationModel):
    service_identifier: str = DjangoModelRef(Service, "slug")
    name: str = DjangoModelRef(ObjectType, "_name")

    class Meta:
        django_model_refs = {
            ObjectType: (
                "uuid",
            )
        }


class ObjectTypesConfigurationModel(ConfigurationModel):
    items: list[ObjectTypeConfigurationModel] = Field()
