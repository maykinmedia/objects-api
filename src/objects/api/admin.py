from django.contrib import admin

from .models import Object


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("object_type", "version")
    search_fields = ("uuid",)
