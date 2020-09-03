from django.contrib import admin

from .constants import RecordType
from .models import Object, ObjectRecord


class ObjectRecordInline(admin.TabularInline):
    model = ObjectRecord
    extra = 0
    readonly_fields = ("registration_date",)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        if not obj:
            return readonly_fields + ("record_type",)

        return readonly_fields

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        formfield = super().formfield_for_choice_field(db_field, request, **kwargs)

        if db_field.name == "record_type":
            choices = [
                choice
                for choice in RecordType.choices
                if choice[0] != RecordType.created
            ]
            formfield.choices = choices

        return formfield


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("object_type", "version", "status")
    search_fields = ("uuid",)
    inlines = (ObjectRecordInline,)

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == RecordType.destroyed:
            return False

        return super().has_change_permission(request, obj)
