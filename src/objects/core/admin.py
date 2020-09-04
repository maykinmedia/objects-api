from django.contrib import admin

from .models import Object, ObjectRecord


class ObjectRecordInline(admin.TabularInline):
    model = ObjectRecord
    extra = 0
    readonly_fields = ("registration_date", "end_date")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("object_type", "version")
    search_fields = ("uuid",)
    inlines = (ObjectRecordInline,)
