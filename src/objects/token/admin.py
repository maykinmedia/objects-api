from django.contrib import admin

from .models import Permission, TokenAuth


class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 1


@admin.register(TokenAuth)
class TokenAuthAdmin(admin.ModelAdmin):
    list_display = ("token", "contact_person", "created")
    inlines = [PermissionInline]
