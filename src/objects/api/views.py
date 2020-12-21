from django.db import models

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from vng_api_common.search import SearchMixin

from objects.accounts.permissions import ObjectBasedPermission
from objects.core.models import Object

from .filters import ObjectFilterSet
from .mixins import GeoMixin
from .serializers import (
    HistoryRecordSerializer,
    ObjectSearchSerializer,
    ObjectSerializer,
)


class ObjectViewSet(SearchMixin, GeoMixin, viewsets.ModelViewSet):
    """
    Manage OBJECTs and their RECORDs.

    list:
    Retrieve a list of OBJECTs and their actual RECORD. The actual record is defined as if the query parameter `date=<today>` was given.

    retrieve:
    Retrieve a single OBJECT and its actual RECORD. The actual record is defined as if the query parameter `date=<today>` was given.

    create:
    Create an OBJECT and its initial RECORD.

    update:
    Update the OBJECT by creating a new RECORD with the updates values.

    partial_update:
    Update the OBJECT by creating a new RECORD with the updates values.

    destroy:
    Delete an OBJECT and all RECORDs belonging to it.

    """

    queryset = Object.objects.prefetch_related("records").order_by("-pk")
    serializer_class = ObjectSerializer
    filterset_class = ObjectFilterSet
    lookup_field = "uuid"
    search_input_serializer_class = ObjectSearchSerializer
    permission_classes = [ObjectBasedPermission]

    def get_queryset(self):
        base = super().get_queryset()

        if self.action not in ("list", "search"):
            return base

        return base.filter_for_date().filter_for_user(self.request.user)

    @swagger_auto_schema(responses={"200": HistoryRecordSerializer(many=True)})
    @action(detail=True, methods=["get"], serializer_class=HistoryRecordSerializer)
    def history(self, request, uuid=None):
        """Retrieve all RECORDs of an OBJECT."""

        records = self.get_object().records.order_by("id")
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def search(self, request):
        """Perform a (geo) search on OBJECTs"""
        search_input = self.get_search_input()

        within = search_input["geometry"]["within"]
        queryset = (
            self.filter_queryset(self.get_queryset())
            .filter(records__geometry__within=within)
            .distinct()
        )

        return self.get_search_output(queryset)

    def get_search_output(self, queryset: models.QuerySet) -> Response:
        """wrapper to make sure the result is a Response subclass"""
        result = super().get_search_output(queryset)

        if not isinstance(result, Response):
            result = Response(result)

        return result

    search.is_search_action = True
