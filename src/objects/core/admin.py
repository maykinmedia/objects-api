import json

from django.contrib import admin
from django.contrib.gis import forms
from django.contrib.gis.db.models import GeometryField

from .models import Object, ObjectRecord, ObjectType


@admin.register(ObjectType)
class ObjectTypeAdmin(admin.ModelAdmin):
    list_display = ("_name", "uuid", "get_version")
    readonly_fields = ("_name",)

    def get_version(self, obj):
        return ObjectRecord.objects.filter(object__object_type=obj).count()

    get_version.short_description = "version"


class ObjectRecordInline(admin.TabularInline):
    model = ObjectRecord
    extra = 1
    formfield_overrides = {GeometryField: {"widget": forms.OSMWidget}}
    readonly_fields = (
        "index",
        "registration_at",
        "end_at",
        "get_corrected_by",
        "get_data_display",
    )
    fields = (
        "version",
        "get_data_display",
        "geometry",
        "start_at",
        "correct",
    ) + ("index", "registration_at", "end_at", "get_corrected_by")

    def get_data_display(self, instance=None):
        if instance:
            return json.dumps(instance.data, indent=4, sort_keys=True)
        return None

    get_data_display.short_description = "data"

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
    list_display = ("id", "object_type", "current_record")
    search_fields = ("uuid",)
    inlines = (ObjectRecordInline,)
    list_filter = ("object_type",)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if obj:
            readonly_fields = ("uuid", "object_type") + readonly_fields

        return readonly_fields
