from django.conf.urls import include
from django.urls import path

from drf_spectacular.views import (
    SpectacularJSONAPIView,
    SpectacularRedocView,
    SpectacularYAMLAPIView,
)
from rest_framework import routers

from .views import ObjectViewSet, PermissionViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"objects", ObjectViewSet)
router.register(r"permissions", PermissionViewSet)

app_name = "v2"

urlpatterns = [
    path("", SpectacularJSONAPIView.as_view(), name="schema-json"),
    path(
        "/",
        include(
            [
                # schema
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
                # actual endpoints
                path("", include(router.urls)),
            ]
        ),
    ),
]
