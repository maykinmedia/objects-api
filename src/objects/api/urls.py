from django.conf.urls import include
from django.urls import path, re_path

from rest_framework import routers
from vng_api_common.schema import SchemaView

from .views import ObjectViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"objects", ObjectViewSet)


urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/",
        include(
            [
                re_path(
                    r"^schema/openapi(?P<format>\.json|\.yaml)$",
                    SchemaView.without_ui(cache_timeout=0),
                    name="schema-json",
                ),
                re_path(
                    r"^schema/$",
                    SchemaView.with_ui("redoc", cache_timeout=0),
                    name="schema-redoc",
                ),
            ]
        ),
    ),
]
