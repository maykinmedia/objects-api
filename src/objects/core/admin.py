from django.contrib import admin
from django.contrib.gis import forms
from django.contrib.gis.db.models import GeometryField

from .models import Object, ObjectRecord


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
    list_display = ("id", "object_type", "current_record")
    search_fields = ("uuid",)
    inlines = (ObjectRecordInline,)
