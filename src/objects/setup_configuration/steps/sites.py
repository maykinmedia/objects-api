from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import ConfigurationRunFailed

from objects.setup_configuration.models.sites import SitesConfigurationModel


class SitesConfigurationStep(BaseConfigurationStep):
    config_model = SitesConfigurationModel
    verbose_name = "Sites configuration"

    namespace = "sites"
    enable_setting = "sites_config_enable"

    def execute(self, model: SitesConfigurationModel) -> None:
        for item in model.items:
            site_kwargs = dict(domain=item.domain, name=item.name)
            site_instance = Site(**site_kwargs)

            try:
                site_instance.full_clean(exclude=("id",), validate_unique=False)
            except ValidationError as exception:
                exception_message = (
                    f"Validation error(s) occured for site {item.domain}."
                )
                raise ConfigurationRunFailed(exception_message) from exception

            try:
                Site.objects.update_or_create(
                    domain=item.domain, defaults=dict(name=item.name)
                )
            except IntegrityError as exception:
                exception_message = f"Failed configuring site {item.domain}."
                raise ConfigurationRunFailed(exception_message) from exception
