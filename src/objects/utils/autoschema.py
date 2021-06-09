from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.utils import OpenApiParameter
from rest_framework import exceptions
from vng_api_common.exceptions import PreconditionFailed
from vng_api_common.geo import DEFAULT_CRS, HEADER_ACCEPT, HEADER_CONTENT
from vng_api_common.inspectors.view import (
    DEFAULT_ACTION_ERRORS,
    HTTP_STATUS_CODE_TITLES,
)
from vng_api_common.search import is_search_view
from vng_api_common.serializers import FoutSerializer, ValidatieFoutSerializer

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

    def _get_response_bodies(self):
        view_responses = super()._get_response_bodies()

        # add responses for error status codes
        view_responses.update(self.get_error_responses())
        return view_responses

    def get_error_responses(self) -> OrderedDict:
        """
        Add the appropriate possible error responses to the schema.

        E.g. - we know that HTTP 400 on a POST/PATCH/PUT leads to validation
        errors, 403 to Permission Denied etc.
        """
        # only supports viewsets
        if not hasattr(self.view, "action"):
            return OrderedDict()

        action = self.view.action
        if action not in DEFAULT_ACTION_ERRORS:
            # search action is similar to create
            if is_search_view(self.view):
                action = "create"
            else:
                action = "list"

        exception_klasses = DEFAULT_ACTION_ERRORS[action][:]
        # add validation errors
        if self._is_list_view() and getattr(self.view, "filter_backends", None):
            exception_klasses.append(exceptions.ValidationError)

        # add geo errors
        if isinstance(self.view, GeoMixin):
            exception_klasses.append(PreconditionFailed)

        status_codes = sorted({e.status_code for e in exception_klasses})

        error_responses = OrderedDict()
        for status_code in status_codes:
            serializer = (
                ValidatieFoutSerializer
                if status_code == exceptions.ValidationError.status_code
                else FoutSerializer
            )
            response = self._get_response_for_code(serializer, str(status_code))
            response["description"] = HTTP_STATUS_CODE_TITLES.get(status_code, "")
            error_responses[status_code] = response

        return error_responses

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
        if any(
            isinstance(serializer, DynamicFieldsMixin)
            for serializer in response_serializers
        ):
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
