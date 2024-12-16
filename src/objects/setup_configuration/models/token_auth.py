from django_setup_configuration.models import ConfigurationModel

from objects.token.models import TokenAuth


class TokenAuthConfigurationModel(ConfigurationModel):
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
