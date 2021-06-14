from django.conf.urls import include
from django.urls import re_path

from drf_spectacular.views import SpectacularJSONAPIView

urlpatterns = [
    re_path(
        r"^v(?P<version>(1))/",
        include("objects.api.v1.urls"),
    ),
    # OAS in the api root
    re_path(
        r"^v(?P<version>\d+)",
        SpectacularJSONAPIView.as_view(),
        name="schema-json",
    ),
]
