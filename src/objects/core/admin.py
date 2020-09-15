from django.contrib import admin

from .models import Object, ObjectRecord


class ObjectRecordInline(admin.TabularInline):
    model = ObjectRecord
    extra = 1
    readonly_fields = ("id", "registration_date", "end_date", "get_after_correction")
    fields = (
        "id",
        "version",
        "data",
        "start_date",
        "end_date",
        "registration_date",
        "correct",
        "get_after_correction",
    )

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

    def get_after_correction(self, obj):
        return obj.corrected

    get_after_correction.short_description = "after correction"


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("object_type",)
    search_fields = ("uuid",)
    inlines = (ObjectRecordInline,)
