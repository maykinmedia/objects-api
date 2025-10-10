from django.urls import include, path

from drf_spectacular.views import (
    SpectacularRedocView,
)
from rest_framework import routers

from objects.utils.oas_extensions.views import (
    DeprecationRedirectView,
    SpectacularJSONAPIView,
    SpectacularYAMLAPIView,
)

from .views import ObjectViewSet, PermissionViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"objects", ObjectViewSet, basename="object")
router.register(r"permissions", PermissionViewSet)

app_name = "v2"

urlpatterns = [
    path(
        "/",
        include(
            [
                path(
                    "schema/openapi.yaml",
                    DeprecationRedirectView.as_view(pattern_name="v2:schema-yaml"),
                ),
                path(
                    "openapi.yaml",
                    SpectacularYAMLAPIView.as_view(),
                    name="schema-yaml",
                ),
                path(
                    "openapi.json",
                    SpectacularJSONAPIView.as_view(),
                    name="schema-json",
                ),
                path(
                    "schema/",
                    SpectacularRedocView.as_view(url_name="schema-yaml"),
                    name="schema-redoc",
                ),
                # actual endpoints
                path("", include(router.urls)),
            ]
        ),
    ),
]
