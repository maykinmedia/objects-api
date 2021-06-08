from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "objects.utils"

    def ready(self):
        from . import checks  # noqa
        from .oas_extensions import (  # noqa
            DjangoFilterExtension,
            GeometryFieldExtension,
        )
