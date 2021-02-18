from drf_yasg import openapi
from drf_yasg.inspectors.base import NotHandled
from drf_yasg.inspectors.field import FieldInspector
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


class ObjectTypeFieldInspector(FieldInspector):
    # separate inspector to specify "format: uri" for this field in OAS
    def field_to_swagger_object(
        self, field, swagger_object_type, use_references, **kwargs
    ):
        SwaggerType, ChildSwaggerType = self._get_partial_types(
            field, swagger_object_type, use_references, **kwargs
        )
        from objects.api.serializers import ObjectTypeField

        if isinstance(field, ObjectTypeField) and swagger_object_type == openapi.Schema:
            return SwaggerType(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
                description=field.help_text,
            )

        return NotHandled
