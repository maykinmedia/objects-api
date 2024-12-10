from django.contrib.sites.models import Site

from django_setup_configuration.models import ConfigurationModel
from pydantic import Field


class SiteConfigurationModel(ConfigurationModel):
    class Meta:
        django_model_refs = {
            Site: (
                "domain",
                "name",
            )
        }


class SitesConfigurationModel(ConfigurationModel):
    items: list[SiteConfigurationModel] = Field()
