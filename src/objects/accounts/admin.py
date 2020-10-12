from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from hijack_admin.admin import HijackUserAdminMixin

from .models import ObjectPermission, User


@admin.register(User)
class _UserAdmin(UserAdmin, HijackUserAdminMixin):
    list_display = UserAdmin.list_display + ("hijack_field",)
    fieldsets = UserAdmin.fieldsets + (
        (_("Object permissions"), {"fields": ("object_permissions",)}),
    )
    raw_id_fields = ("object_permissions",)


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    list_display = ("object_type", "mode")
