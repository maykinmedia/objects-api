from django.conf.urls import include
from django.urls import path, re_path

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularYAMLAPIView,
)
from rest_framework import routers

from .views import ObjectViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"objects", ObjectViewSet)


urlpatterns = [
    re_path(
        r"^v(?P<version>\d+)/",
        include(
            [
                path("", include(router.urls)),
                path(
                    "schema/openapi.yaml",
                    SpectacularYAMLAPIView.as_view(),
                    name="schema",
                ),
                path(
                    "schema/",
                    SpectacularRedocView.as_view(url_name="schema"),
                    name="schema-redoc",
                ),
            ]
        ),
    ),
    re_path(
        r"^v(?P<version>\d+)",
        SpectacularJSONAPIView.as_view(),
        name="schema-json",
    ),
]
