import warnings

from django.views.generic import RedirectView

import structlog
from drf_spectacular.views import (
    SpectacularJSONAPIView as _SpectacularJSONAPIView,
    SpectacularYAMLAPIView as _SpectacularYAMLAPIView,
)

logger = structlog.stdlib.get_logger(__name__)


class AllowAllOriginsMixin:
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        return response


class SpectacularYAMLAPIView(AllowAllOriginsMixin, _SpectacularYAMLAPIView):
    """Spectacular YAML API view with Access-Control-Allow-Origin set to allow all"""


class SpectacularJSONAPIView(AllowAllOriginsMixin, _SpectacularJSONAPIView):
    """Spectacular JSON API view with Access-Control-Allow-Origin set to allow all"""


class DeprecationRedirectView(RedirectView):
    def get(self, request, *args, **kwargs):
        warnings.warn(
            "api/v2/schema/openapi.yaml has been moved to api/v2/openapi.yaml and will be removed in the next release.",
            DeprecationWarning,
        )
        return super().get(request, *args, **kwargs)
