from drf_yasg import openapi
from vng_api_common.geo import DEFAULT_CRS, HEADER_ACCEPT, HEADER_CONTENT
from vng_api_common.inspectors.geojson import (
    GeometryFieldInspector as _GeometryFieldInspector,
)


class GeometryFieldInspector(_GeometryFieldInspector):
    """ don't show GEO headers since they are not required now"""

    def get_request_header_parameters(self, serializer):
        if not self.has_geo_fields(serializer):
            return []

        if self.method == "DELETE":
            return []

        headers = [
            openapi.Parameter(
                name=HEADER_ACCEPT,
                type=openapi.TYPE_STRING,
                in_=openapi.IN_HEADER,
                required=False,
                description="Het gewenste 'Coordinate Reference System' (CRS) van de "
                "geometrie in het antwoord (response body). Volgens de "
                "GeoJSON spec is WGS84 de default (EPSG:4326 is "
                "hetzelfde als WGS84).",
                enum=[DEFAULT_CRS],
            ),
        ]

        if self.method in ("POST", "PUT", "PATCH"):
            headers.append(
                openapi.Parameter(
                    name=HEADER_CONTENT,
                    type=openapi.TYPE_STRING,
                    in_=openapi.IN_HEADER,
                    required=True,
                    description="Het 'Coordinate Reference System' (CRS) van de "
                    "geometrie in de vraag (request body). Volgens de "
                    "GeoJSON spec is WGS84 de default (EPSG:4326 is "
                    "hetzelfde als WGS84).",
                    enum=[DEFAULT_CRS],
                ),
            )

        return headers
