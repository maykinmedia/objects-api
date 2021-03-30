from django.conf.urls import include
from django.urls import path, re_path

from drf_yasg.renderers import SwaggerJSONRenderer
from rest_framework import routers
from vng_api_common.schema import SPEC_RENDERERS, SchemaView

from .views import ObjectViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"objects", ObjectViewSet)


class JsonSchemaView(SchemaView):
    @property
    def _is_openapi_v2(self) -> bool:
        return False

    def get_renderers(self):
        # only json renderers
        renderers = [
            renderer()
            for renderer in SPEC_RENDERERS
            if isinstance(renderer(), SwaggerJSONRenderer)
        ]
        return renderers


urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/",
        include(
            [
                re_path(
                    r"^schema/openapi(?P<format>\.json|\.yaml)$",
                    SchemaView.without_ui(cache_timeout=0),
                    name="schema-yaml",
                ),
                re_path(
                    r"^schema/$",
                    SchemaView.with_ui("redoc", cache_timeout=0),
                    name="schema-redoc",
                ),
            ]
        ),
    ),
    path(
        "v1",
        JsonSchemaView.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]
