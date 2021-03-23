from django.utils.translation import ugettext_lazy as _

from drf_yasg import openapi
from drf_yasg.inspectors.base import NotHandled
from drf_yasg.inspectors.field import FieldInspector
from rest_framework import serializers
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
                description=_(
                    "The desired 'Coordinate Reference System' (CRS) of the response data. "
                    "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                    "is the same as WGS84)."
                ),
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
                    description=_(
                        "The 'Coordinate Reference System' (CRS) of the request data. "
                        "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                        "is the same as WGS84)."
                    ),
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
                min_length=field.min_length,
                max_length=field.max_length,
            )

        return NotHandled


class HyperlinkedIdentityFieldInspector(FieldInspector):
    # copied from vng_api_common.inspectors.HyperlinkedIdentityFieldInspector
    # with the change of description
    def field_to_swagger_object(
        self, field, swagger_object_type, use_references, **kwargs
    ):
        SwaggerType, ChildSwaggerType = self._get_partial_types(
            field, swagger_object_type, use_references, **kwargs
        )

        if (
            isinstance(field, serializers.HyperlinkedIdentityField)
            and swagger_object_type == openapi.Schema
        ):
            return SwaggerType(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_URI,
                min_length=1,
                max_length=1000,
                description=_(
                    "URL reference to this object. This is the unique identification "
                    "and location of this object."
                ),
            )

        return NotHandled
