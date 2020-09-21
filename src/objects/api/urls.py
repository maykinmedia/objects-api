from django.conf.urls import include
from django.urls import path, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from .views import ObjectViewSet

router = routers.DefaultRouter()
router.register(r"objects", ObjectViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Objects API",
        default_version="v1",
        description="OAS for Objects API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/",
        include(
            [
                re_path(
                    r"^openapi(?P<format>\.json|\.yaml)$",
                    schema_view.without_ui(cache_timeout=0),
                    name="schema-json",
                ),
                re_path(
                    r"^schema/$",
                    schema_view.with_ui("redoc", cache_timeout=0),
                    name="schema-redoc",
                ),
            ]
        ),
    ),
]
