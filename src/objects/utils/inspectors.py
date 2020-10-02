from vng_api_common.inspectors.geojson import (
    GeometryFieldInspector as _GeometryFieldInspector,
)


class GeometryFieldInspector(_GeometryFieldInspector):
    """ don't show GEO headers since they are not required now"""

    def get_request_header_parameters(self, serializer):
        return []

    def get_response_headers(self, serializer, status=None):
        return None
