from typing import Sequence

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.db.models import GeometryField
from django.db.models import CharField
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast
from django.http import HttpRequest, JsonResponse
from django.urls import path

import requests
import structlog
from vng_api_common.utils import get_help_text

from objects.utils.client import get_objecttypes_client

from .models import Object, ObjectRecord, ObjectType

logger = structlog.stdlib.get_logger(__name__)


@admin.register(ObjectType)
class ObjectTypeAdmin(admin.ModelAdmin):
    list_display = (
        "_name",
        "uuid",
    )
    readonly_fields = ("_name",)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "<int:objecttype_id>/_versions/",
                self.admin_site.admin_view(self.versions_view),
                name="objecttype_versions",
            )
        ]
        return my_urls + urls

    def versions_view(self, request, objecttype_id):
        versions = []
        if objecttype := self.get_object(request, objecttype_id):
            with get_objecttypes_client(objecttype.service) as client:
                try:
                    versions = client.list_objecttype_versions(objecttype.uuid)
                except (requests.RequestException, requests.JSONDecodeError) as exc:
                    logger.exception("objecttypes_api_request_failure", exc_info=exc)
        return JsonResponse(versions, safe=False)


class ObjectRecordForm(forms.ModelForm):
    class Meta:
        model: ObjectRecord
        help_texts = {
            "geometry": get_help_text("core.ObjectRecord", "geometry")
            + "\n\n format: SRID=4326;POINT|LINESTRING|POLYGON (LAT LONG, ...)"
        }
        fields = "__all__"


class ObjectRecordInline(admin.TabularInline):
    form = ObjectRecordForm
    model = ObjectRecord
    extra = 1
    readonly_fields = (
        "index",
        "registration_at",
        "end_at",
        "get_corrected_by",
        "created_on",
        "modified_on",
    )
    fields = (
        "index",
        "version",
        "data",
        "geometry",
        "start_at",
        "end_at",
        "registration_at",
        "get_corrected_by",
        "correct",
        "created_on",
        "modified_on",
    )

    formfield_overrides = {GeometryField: {"widget": forms.Textarea}}

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "correct":
            object_id = request.resolver_match.kwargs.get("object_id")
            if not object_id:
                kwargs["queryset"] = ObjectRecord.objects.none()
            else:
                kwargs["queryset"] = ObjectRecord.objects.filter(
                    object_id=int(object_id), corrected__isnull=True
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_corrected_by(self, obj):
        return obj.corrected

    get_corrected_by.short_description = "corrected by"


class ObjectTypeFilter(SimpleListFilter):
    """
    List filters do not use `ModelAdmin.list_select_related` unfortunately, so to avoid
    additional queries for each ObjectType.service, the filter's queryset is explicitly
    overridden
    """

    title = "object type"
    parameter_name = "object_type__id__exact"

    def lookups(self, request, model_admin):
        qs = ObjectType.objects.select_related("service")
        return [(ot.pk, str(ot)) for ot in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(object_type__id=self.value())
        return queryset


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "object_type",
        "current_record",
        "uuid",
        "get_object_type_uuid",
        "modified_on",
        "created_on",
    )
    search_fields = ("uuid",)
    inlines = (ObjectRecordInline,)
    list_filter = (ObjectTypeFilter, "created_on", "modified_on")

    def get_search_fields(self, request: HttpRequest) -> Sequence[str]:
        if settings.OBJECTS_ADMIN_SEARCH_DISABLED:
            return ()

        return ("uuid",)

    def get_search_results(self, request, queryset, search_term):
        if settings.OBJECTS_ADMIN_SEARCH_DISABLED:
            return queryset, False

        if ":" in search_term:
            key, _, value = search_term.partition(":")
            key = key.strip()
            value = value.strip()

            queryset = queryset.filter(records__data__has_key=key)

            queryset = queryset.annotate(
                key_text=Cast(KeyTextTransform(key, "records__data"), CharField())
            ).filter(key_text__icontains=value)

            return queryset.distinct(), False

        return super().get_search_results(request, queryset, search_term)

    @admin.display(description="Object type UUID")
    def get_object_type_uuid(self, obj):
        return obj.object_type.uuid

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj:
            readonly_fields = (
                "uuid",
                "get_object_type_uuid",
                "object_type",
                "created_on",
                "modified_on",
            ) + readonly_fields

        return readonly_fields
