from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from drf_spectacular.extensions import OpenApiFilterExtension
from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.plumbing import build_parameter_type, get_view_model
from drf_spectacular.utils import OpenApiParameter
from vng_api_common.geo import DEFAULT_CRS, HEADER_ACCEPT, HEADER_CONTENT
from vng_api_common.inspectors.view import HTTP_STATUS_CODE_TITLES

from objects.api.mixins import GeoMixin

from .serializers import DynamicFieldsMixin

object_path_parameter = OpenApiParameter(
    name="object__uuid", required=True, location=OpenApiParameter.PATH
)


class AutoSchema(_AutoSchema):
    def get_operation_id(self):
        """
        Use model name as a base for operation_id
        """
        if hasattr(self.view, "basename"):
            basename = self.view.basename
            return f"{basename}_{self.view.action}"
        return super().get_operation_id()

    def get_override_parameters(self):
        """Add request GEO headers"""
        geo_headers = self.get_geo_headers()
        content_type_headers = self.get_content_type_headers()
        field_params = self.get_fields_params()
        return geo_headers + content_type_headers + field_params

    def _get_filter_parameters(self):
        """remove filter parameters from all actions except LIST"""
        if self.view.action != "list":
            return []
        return super()._get_filter_parameters()

    def _get_response_for_code(self, serializer, status_code, media_types=None):
        """add default description to the response"""
        response = super()._get_response_for_code(serializer, status_code, media_types)

        if not response.get("description"):
            response["description"] = HTTP_STATUS_CODE_TITLES.get(int(status_code))
        return response

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
                        "For example: 'url, uuid, record__geometry'."
                    ),
                ),
                OpenApiParameter(
                    name=settings.UNAUTHORIZED_FIELDS_HEADER,
                    type=str,
                    location=OpenApiParameter.HEADER,
                    response=True,
                    description=_(
                        "List of fields that are not allowed to display if the field-based "
                        "authorization is turned on. The value has the following format: "
                        "`objectType1:fieldA,fieldB; objectType2:fieldC,fieldD`"
                    ),
                ),
            ]

        return []

    def _get_request_body(self):
        """update search request body with filter parameters"""
        request_body = super()._get_request_body()

        if self.view.action == "search":
            filter_params = self.get_filter_params_for_search()

            properties = {}
            for param in filter_params:
                schema = param["schema"]
                schema["description"] = param["description"]
                properties[param["name"]] = schema

            filter_schema = {"type": "object", "properties": properties}

            for media_type, media_value in request_body["content"].items():
                request_body["content"][media_type]["schema"] = {
                    "type": "object",
                    "allOf": [media_value["schema"], filter_schema],
                }

        return request_body

    def get_filter_params_for_search(self):
        """copy paste of self._get_filter_parameters() without conditions"""
        parameters = []
        for filter_backend in self.view.filter_backends:
            filter_extension = OpenApiFilterExtension.get_match(filter_backend())
            if filter_extension:
                parameters += filter_extension.get_schema_operation_parameters(self)
            else:
                parameters += filter_backend().get_schema_operation_parameters(
                    self.view
                )
        return parameters

    def _resolve_path_parameters(self, variables):
        object_path = "uuid"
        if variables == [object_path] and self.view.basename == "object":
            model = get_view_model(self.view)
            object_field = model._meta.get_field("object")
            uuid_field = object_field.related_model._meta.get_field("uuid")
            schema = self._map_model_field(uuid_field, direction=None)

            return [
                build_parameter_type(
                    name=object_path, location=OpenApiParameter.PATH, schema=schema
                )
            ]

        return super()._resolve_path_parameters(variables)
