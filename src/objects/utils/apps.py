from django.apps import AppConfig
from django.db import models

from drf_spectacular.extensions import OpenApiFilterExtension
from rest_framework.serializers import ModelSerializer

from .fields import JSONObjectField


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
        from . import oas_extensions  # noqa
        from ..api import metrics  # noqa

        unregister_camelize_filter_extension()

        field_mapping = ModelSerializer.serializer_field_mapping
        field_mapping[models.JSONField] = JSONObjectField
