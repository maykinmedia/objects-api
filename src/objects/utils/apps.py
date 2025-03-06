from django.apps import AppConfig

from drf_spectacular.extensions import OpenApiFilterExtension


def unregister_camelize_filter_extension():
    """
    CamelizeFilterExtension from vng_api_common is loaded automatically
    and cannot be removed using SPECTACULAR_SETTINGS.
    """
    OpenApiFilterExtension._registry = [
        ext
        for ext in OpenApiFilterExtension._registry
        if ext.__name__ != "CamelizeFilterExtension"
    ]


class UtilsConfig(AppConfig):
    name = "objects.utils"

    def ready(self):
        from . import checks  # noqa
        from . import oas_extensions  # noqa

        unregister_camelize_filter_extension()
