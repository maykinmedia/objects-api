import datetime

from django.conf import settings
from django.db import models

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from vng_api_common.filters import Backend as FilterBackend
from vng_api_common.notifications.viewsets import NotificationViewSetMixin
from vng_api_common.search import SearchMixin

from objects.core.models import Object, ObjectRecord
from objects.token.models import Permission
from objects.token.permissions import ObjectTypeBasedPermission

from ..filter_backends import OrderingBackend
from ..kanalen import KANAAL_OBJECTEN
from ..mixins import GeoMixin
from ..pagination import DynamicPageSizePagination
from ..serializers import (
    HistoryRecordSerializer,
    ObjectSearchSerializer,
    ObjectSerializer,
    PermissionSerializer,
)
from .filters import ObjectRecordFilterSet


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of OBJECTs and their actual RECORD. "
        "The actual record is defined as if the query parameter `date=<today>` was given."
    ),
    retrieve=extend_schema(
        description="Retrieve a single OBJECT and its actual RECORD. "
        "The actual record is defined as if the query parameter `date=<today>` was given.",
        operation_id="object_read",
    ),
    create=extend_schema(description="Create an OBJECT and its initial RECORD."),
    update=extend_schema(
        description="Update the OBJECT by creating a new RECORD with the updates values."
    ),
    partial_update=extend_schema(
        description="Update the OBJECT by creating a new RECORD with the updates values."
    ),
    destroy=extend_schema(
        description="Delete an OBJECT and all RECORDs belonging to it.",
        operation_id="object_delete",
    ),
)
class ObjectViewSet(
    NotificationViewSetMixin, SearchMixin, GeoMixin, viewsets.ModelViewSet
):
    queryset = Object.objects.select_related(
        "object_type", "object_type__service"
    ).order_by("-pk")
    serializer_class = ObjectSerializer
    filter_backends = [FilterBackend, OrderingBackend]
    filterset_class = ObjectRecordFilterSet
    ordering_fields = "__all__"
    lookup_field = "uuid"
    search_input_serializer_class = ObjectSearchSerializer
    permission_classes = [ObjectTypeBasedPermission]
    pagination_class = DynamicPageSizePagination
    notifications_kanaal = KANAAL_OBJECTEN

    def get_queryset(self):
        base = super().get_queryset()

        # `vng_api_common.utils.get_viewset_for_path` passes an empty request
        # object that does not have `query_params` and 'auth'
        date = getattr(self.request, "query_params", {}).get("date", None)
        registration_date = getattr(self.request, "query_params", {}).get(
            "registrationDate", None
        )
        token_auth = getattr(self.request, "auth", None)

        # prefetch filtered records as actual ones for DB optimization
        record_queryset = (
            ObjectRecord.objects.filter_for_registration_date(registration_date)
            if registration_date and not date
            else ObjectRecord.objects.filter_for_date(date or datetime.date.today())
        )
        base = base.prefetch_related(
            models.Prefetch(
                "records",
                queryset=record_queryset.select_related("correct", "corrected"),
                to_attr="actual_records",
            ),
            models.Prefetch(
                "object_type__permissions",
                queryset=Permission.objects.filter(token_auth=token_auth),
                to_attr="token_permissions",
            ),
        )

        if self.action not in ("list", "search"):
            return base

        return base.filter_for_token(self.request.auth)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            if backend == FilterBackend:
                queryset = self.filter_queryset_on_records(queryset)
            else:
                queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def filter_queryset_on_records(self, queryset):
        """ filter records first"""
        records = ObjectRecord.objects.select_related("object")
        filtered_records = FilterBackend().filter_queryset(self.request, records, self)

        date = getattr(self.request, "query_params", {}).get("date", None)
        registration_date = getattr(self.request, "query_params", {}).get(
            "registrationDate", None
        )
        if self.action in ("list", "search") and not date and not registration_date:
            filtered_records = filtered_records.filter_for_date(datetime.date.today())

        return queryset.filter(records__in=filtered_records).distinct()

    @extend_schema(
        description="Retrieve all RECORDs of an OBJECT.",
        responses={"200": HistoryRecordSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], serializer_class=HistoryRecordSerializer)
    def history(self, request, uuid=None):
        """Retrieve all RECORDs of an OBJECT."""
        records = self.get_object().records.order_by("id")
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="Perform a (geo) search on OBJECTs.",
        request=ObjectSearchSerializer,
        responses={"200": ObjectSerializer(many=True)},
    )
    @action(detail=False, methods=["post"])
    def search(self, request):
        """Perform a (geo) search on OBJECTs"""
        search_input = self.get_search_input()
        queryset = self.filter_queryset(self.get_queryset())

        if "geometry" in search_input:
            within = search_input["geometry"]["within"]
            queryset = queryset.filter(records__geometry__within=within).distinct()

        return self.get_search_output(queryset)

    def get_search_output(self, queryset: models.QuerySet) -> Response:
        """wrapper to make sure the result is a Response subclass"""
        result = super().get_search_output(queryset)

        if not isinstance(result, Response):
            result = Response(result)

        return result

    # for OAS generation
    search.is_search_action = True

    def finalize_response(self, request, response, *args, **kwargs):
        """add warning header if not all data is allowed to display"""

        if response.status_code == 200:
            serializer = getattr(response.data, "serializer", None) or getattr(
                response.data.get("results"), "serializer", None
            )
            if self.action == "retrieve" and serializer.not_allowed:
                self.headers[
                    settings.UNAUTHORIZED_FIELDS_HEADER
                ] = serializer.not_allowed.pretty()

            elif self.action in ("list", "search") and serializer.child.not_allowed:
                self.headers[
                    settings.UNAUTHORIZED_FIELDS_HEADER
                ] = serializer.child.not_allowed.pretty()

        return super().finalize_response(request, response, *args, **kwargs)


@extend_schema_view(
    list=extend_schema(
        description="Retrieve a list of permissions available for the user"
    )
)
class PermissionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Permission.objects.select_related("object_type", "token_auth").order_by(
        "object_type"
    )
    serializer_class = PermissionSerializer
    lookup_field = "uuid"
    search_input_serializer_class = ObjectSearchSerializer
    pagination_class = DynamicPageSizePagination

    def get_queryset(self):
        queryset = super().get_queryset()

        # show permissions for the current user
        return queryset.filter(token_auth=self.request.auth)
