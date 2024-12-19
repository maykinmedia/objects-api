from django_setup_configuration.fields import DjangoModelRef
from django_setup_configuration.models import ConfigurationModel
from pydantic import UUID4, Field

from objects.token.models import Permission, TokenAuth


class TokenAuthPermissionConfigurationModel(ConfigurationModel):
    object_type: UUID4
    fields: dict[str, list[str]] | None = DjangoModelRef(
        Permission, "fields", default=None
    )

    class Meta:
        django_model_refs = {
            Permission: (
                "mode",
                "use_fields",
            ),
        }


class TokenAuthConfigurationModel(ConfigurationModel):
    permissions: list[TokenAuthPermissionConfigurationModel] | None = Field(
        default_factory=list,
    )

    class Meta:
        django_model_refs = {
            TokenAuth: (
                "identifier",
                "token",
                "contact_person",
                "email",
                "organization",
                "application",
                "administration",
                "is_superuser",
            )
        }


class TokenAuthGroupConfigurationModel(ConfigurationModel):
    items: list[TokenAuthConfigurationModel]
