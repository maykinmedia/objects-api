from django.utils.translation import ugettext_lazy as _

from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.utils import OpenApiParameter
from vng_api_common.geo import DEFAULT_CRS, HEADER_ACCEPT, HEADER_CONTENT

from objects.api.mixins import GeoMixin

from .serializers import DynamicFieldsMixin


class AutoSchema(_AutoSchema):
    def get_operation_id(self):
        """
        Use model name as a base for operation_id
        """
        if hasattr(self.view, "queryset"):
            model_name = self.view.queryset.model._meta.model_name
            return f"{model_name}_{self.view.action}"
        return super().get_operation_id()

    def get_override_parameters(self):
        """ Add request GEO headers"""
        geo_headers = self.get_geo_headers()
        content_type_headers = self.get_content_type_headers()
        field_params = self.get_fields_params()
        return geo_headers + content_type_headers + field_params

    def get_geo_headers(self) -> list:
        if not isinstance(self.view, GeoMixin):
            return []

        request_headers = []
        if self.method != "DELETE":
            request_headers.append(
                OpenApiParameter(
                    name=HEADER_ACCEPT,
                    type=str,
                    location=OpenApiParameter.HEADER,
                    required=False,
                    description=_(
                        "The desired 'Coordinate Reference System' (CRS) of the response data. "
                        "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                        "is the same as WGS84)."
                    ),
                    enum=[DEFAULT_CRS],
                )
            )

        if self.method in ("POST", "PUT", "PATCH"):
            request_headers.append(
                OpenApiParameter(
                    name=HEADER_CONTENT,
                    type=str,
                    location=OpenApiParameter.HEADER,
                    required=True,
                    description=_(
                        "The 'Coordinate Reference System' (CRS) of the request data. "
                        "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                        "is the same as WGS84)."
                    ),
                    enum=[DEFAULT_CRS],
                ),
            )

        response_headers = [
            OpenApiParameter(
                name=HEADER_CONTENT,
                type=str,
                location=OpenApiParameter.HEADER,
                description=_(
                    "The 'Coordinate Reference System' (CRS) of the request data. "
                    "According to the GeoJSON spec, WGS84 is the default (EPSG: 4326 "
                    "is the same as WGS84)."
                ),
                enum=[DEFAULT_CRS],
                response=[200, 201],
            )
        ]

        return request_headers + response_headers

    def get_content_type_headers(self) -> list:
        if self.method not in ["POST", "PUT", "PATCH"]:
            return []

        return [
            OpenApiParameter(
                name="Content-Type",
                type=str,
                location=OpenApiParameter.HEADER,
                required=True,
                enum=["application/json"],
                description=_("Content type of the request body."),
            )
        ]

    def get_fields_params(self) -> []:
        if self.method != "GET":
            return []

        response_serializers = self.get_response_serializers()
        if isinstance(response_serializers, DynamicFieldsMixin):
            return [
                OpenApiParameter(
                    name="fields",
                    type=str,
                    location=OpenApiParameter.QUERY,
                    required=False,
                    description=_(
                        "Comma-separated fields, which should be displayed in the response. "
                        "For example: 'url, uuid, record__geometry'. Attributes inside `record.data` "
                        "field are not supported for this parameter. "
                    ),
                )
            ]

        return []
