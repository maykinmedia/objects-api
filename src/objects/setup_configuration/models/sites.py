from django.contrib.sites.models import Site

from django_setup_configuration.models import ConfigurationModel


class SiteConfigurationModel(ConfigurationModel):
    class Meta:
        django_model_refs = {
            Site: (
                "domain",
                "name",
            )
        }


class SitesConfigurationModel(ConfigurationModel):
    items: list[SiteConfigurationModel]
