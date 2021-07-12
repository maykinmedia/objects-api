from django.contrib import admin

from objects.utils.admin import EditInlineAdminMixin

from .models import Permission, TokenAuth


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("token_auth", "object_type", "mode", "use_fields")


class PermissionInline(EditInlineAdminMixin, admin.TabularInline):
    model = Permission


@admin.register(TokenAuth)
class TokenAuthAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "contact_person",
        "organization",
        "administration",
        "application",
    )
    readonly_fields = ("token",)
    inlines = [PermissionInline]
