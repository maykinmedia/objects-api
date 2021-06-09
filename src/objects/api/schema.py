import logging
from collections import OrderedDict

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.utils import OpenApiParameter
from drf_yasg import openapi
from rest_framework import exceptions
from vng_api_common.exceptions import PreconditionFailed
from vng_api_common.geo import DEFAULT_CRS, HEADER_ACCEPT, HEADER_CONTENT
from vng_api_common.inspectors.view import (
    DEFAULT_ACTION_ERRORS,
    HTTP_STATUS_CODE_TITLES,
)
from vng_api_common.search import is_search_view
from vng_api_common.serializers import FoutSerializer, ValidatieFoutSerializer

from .mixins import GeoMixin

logger = logging.getLogger(__name__)

description = """An API to manage Objects.

# Introduction

An OBJECT is of a certain OBJECTTYPE (defined in the Objecttypes API). An
OBJECT has a few core attributes that every OBJECT (technically a RECORD,
see below) has, although these attributes can sometimes be empty. They are
attributes like `geometry` and some administrative attributes. The data that
describes the actual object is stored in the `data` attribute and follows
the JSON schema as given by the OBJECTTYPE.

## Validation

When an OBJECT is created or changed the `OBJECT.type` attribute refers to the
matching OBJECTTYPE in the Objecttypes API. The RECORD always indicates which
OBJECTTYPE-VERSION is used, shown in the `RECORD.typeVersion` attribute.

Using these 2 attributes, the appropriate JSON schema is retrieved from the
Objecttypes API and the OBJECT data is validated against this JSON schema.

## History

Each OBJECT has 1 or more RECORDs. A RECORD contains the data of an OBJECT
at a certain time. An OBJECT can have multiple RECORDS that describe the
history of that OBJECT. Changes to an OBJECT actually create a new RECORD
under the OBJECT and leaves the old RECORD as is.

### Material and formal history

History can be seen from 2 perspectives: material and formal history. The
material history describes the history as it should be (stored in the
`startAt` and `endAt` attributes). The formal history describes the
history as it was administratively processed (stored in the `registeredAt`
attribute).

The difference is that an object could be created or updated in the real
world at a certain point in time but the administrative change (ie. save or
update the object in the Objects API) can be done at a later time. The
query parameters `?date=2021-01-01` (material history) and
`?registrationDate=2021-01-01` (formal history) allow for querying the
RECORDS as seen from both perspectives, and can yield different results.

### Corrections

RECORDs cannot be deleted or changed once saved. If an error was made to
a RECORD, the RECORD can be "corrected" by saving a new RECORD and indicate
that it corrects a previous RECORD. This is done via the attribute
`correctionFor`.

### Deletion

Although OBJECTs can be deleted, it is sometimes better to set the
`endDate` of an OBJECT. Deleting an OBJECT also deletes all RECORDs in
accordance with privacy laws.

# Authorizations

The API uses API-tokens that grant certain permissions. The API-token is
passed via a header, like this: `Authorization: Token <token>`
"""

info = openapi.Info(
    title=f"{settings.PROJECT_NAME} API",
    default_version=settings.API_VERSION,
    description=description,
)


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
        return geo_headers + content_type_headers

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
                location=openapi.IN_HEADER,
                required=True,
                enum=["application/json"],
                description=_("Content type of the request body."),
            )
        ]
