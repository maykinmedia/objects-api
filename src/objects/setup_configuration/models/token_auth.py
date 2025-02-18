from django_setup_configuration.fields import DjangoModelRef
from django_setup_configuration.models import ConfigurationModel
from pydantic import UUID4, Field

from objects.token.models import Permission, TokenAuth


class TokenAuthPermissionConfigurationModel(ConfigurationModel):
    object_type: UUID4 = Field(
        description="The UUID of the objecttype for which permission will be configured for this token."
    )
    fields: dict[str, list[str]] | None = DjangoModelRef(
        Permission,
        "fields",
        default=None,
        examples=[{"1": ["record__data__leeftijd", "record__data__kiemjaar"]}],
        description=(
            "The fields to which this token has access (field-based authorization). "
            "Note that this can only be specified if the permission mode is `read_only` "
            "and use_fields is set to `true`."
        ),
    )

    class Meta:
        django_model_refs = {
            Permission: (
                "mode",
                "use_fields",
            ),
        }
        extra_kwargs = {
            "use_fields": {
                "examples": [True],
            },
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
