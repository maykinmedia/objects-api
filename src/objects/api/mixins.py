from rest_framework.exceptions import NotAcceptable
from rest_framework.renderers import BrowsableAPIRenderer
from vng_api_common.exceptions import PreconditionFailed
from vng_api_common.geo import (
    DEFAULT_CRS,
    HEADER_ACCEPT,
    HEADER_CONTENT,
    GeoMixin as _GeoMixin,
    extract_header,
)


class GeoMixin(_GeoMixin):
    def perform_crs_negotation(self, request):
        # don't cripple the browsable API...
        if isinstance(request.accepted_renderer, BrowsableAPIRenderer):
            return

        # methods with request bodies need to have the CRS specified
        if request.method.lower() in ("post", "put", "patch"):
            content_crs = extract_header(request, HEADER_CONTENT)
            if content_crs is None:
                raise PreconditionFailed(detail=f"'{HEADER_CONTENT}' header ontbreekt")
            if content_crs != DEFAULT_CRS:
                raise NotAcceptable(detail=f"CRS '{content_crs}' is niet ondersteund")

        if request.method.lower() == "delete":
            return

        # check optional header
        requested_crs = extract_header(request, HEADER_ACCEPT)
        if requested_crs and requested_crs != DEFAULT_CRS:
            raise NotAcceptable(detail=f"CRS '{requested_crs}' is niet ondersteund")
