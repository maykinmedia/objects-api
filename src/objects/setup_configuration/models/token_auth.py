from django_setup_configuration.models import ConfigurationModel
from pydantic import UUID4, Field

from objects.token.models import Permission, TokenAuth


class TokenAuthPermissionConfigurationModel(ConfigurationModel):
    object_type: UUID4 = Field(
        description="The UUID of the objecttype for which permission will be configured for this token."
    )

    class Meta:
        django_model_refs = {
            Permission: ("mode",),
        }


class TokenAuthConfigurationModel(ConfigurationModel):
    permissions: list[TokenAuthPermissionConfigurationModel] | None = Field(
        default_factory=list, description="List of permissions for this token."
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
        extra_kwargs = {
            "identifier": {
                "examples": ["application-name"],
            },
            "token": {
                "examples": ["modify-this"],
            },
        }


class TokenAuthGroupConfigurationModel(ConfigurationModel):
    items: list[TokenAuthConfigurationModel]
