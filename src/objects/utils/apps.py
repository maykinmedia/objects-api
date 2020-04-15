from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "objects.utils"

    def ready(self):
        from . import checks  # noqa
