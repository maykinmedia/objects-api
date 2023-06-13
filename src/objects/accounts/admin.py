from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from hijack.contrib.admin import HijackUserAdminMixin

from .models import User


@admin.register(User)
class _UserAdmin(UserAdmin, HijackUserAdminMixin):
    list_display = UserAdmin.list_display + ("hijack_field",)
