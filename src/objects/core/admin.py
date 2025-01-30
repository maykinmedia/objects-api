import logging

from django.contrib import admin
from django.contrib.gis import forms
from django.contrib.gis.db.models import GeometryField
from django.http import JsonResponse
from django.urls import path

import requests
from zgw_consumers.client import build_client
from zgw_consumers.service import pagination_helper

from .models import Object, ObjectRecord, ObjectType

logger = logging.getLogger(__name__)


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
            client = build_client(objecttype.service)
            try:
                response = client.get(objecttype.versions_url)
                versions = list(pagination_helper(client, response.json()))
            except (requests.RequestException, requests.JSONDecodeError):
                logger.exception(
                    "Something went wrong while fetching objecttype versions"
                )
        return JsonResponse(versions, safe=False)


class ObjectRecordInline(admin.TabularInline):
    model = ObjectRecord
    extra = 1
    readonly_fields = ("index", "registration_at", "end_at", "get_corrected_by")
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
    )
    formfield_overrides = {GeometryField: {"widget": forms.OSMWidget}}

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


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "object_type",
        "current_record",
        "uuid",
        "get_object_type_uuid",
    )
    search_fields = ("uuid", "records__data")
    inlines = (ObjectRecordInline,)
    list_filter = ("object_type",)

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
            ) + readonly_fields

        return readonly_fields
