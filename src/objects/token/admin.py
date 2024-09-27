from django.contrib import admin, messages
from django.contrib.admin.utils import unquote
from django.utils.translation import gettext_lazy as _

import requests
from zgw_consumers.client import build_client

from objects.api.serializers import ObjectSerializer
from objects.core.models import ObjectType
from objects.core.utils import can_connect_to_objecttypes
from objects.utils.admin import EditInlineAdminMixin
from objects.utils.serializers import build_spec, get_field_names

from .constants import PermissionModes
from .models import Permission, TokenAuth

EMPTY_FIELD_CHOICE = ("", "---------")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "token_auth",
        "object_type",
        "mode",
        "use_fields",
        "get_uuid",
    )

    @admin.display(description="Object type UUID")
    def get_uuid(self, obj):
        return obj.object_type.uuid

    def get_object_fields(self):
        object_serializer = ObjectSerializer()
        object_fields = build_spec(get_field_names(object_serializer.fields), ui=True)
        return object_fields

    def get_data_field_choices(self):
        data_fields = {}
        for object_type in ObjectType.objects.all():
            client = build_client(object_type.service)
            url = f"{object_type.url}/versions"

            try:
                response = client.get(url)
            except requests.RequestException:
                continue

            try:
                response_data = response.json()
            except requests.JSONDecodeError:
                continue

            # TODO: remove check once API V1 is removed
            if "results" in response_data:
                response_data = response_data["results"]

            # use only first level of properties
            data_fields[object_type.id] = {
                version["version"]: {
                    prop: f"record__data__{prop}"
                    for prop in list(version["jsonSchema"].get("properties", {}).keys())
                }
                for version in response_data
            }

        return data_fields

    def get_form_data(self, request, object_id) -> dict:
        obj = self.get_object(request, unquote(object_id)) if object_id else None
        ModelForm = self.get_form(request, obj, change=not obj)
        if request.method == "POST":
            form = ModelForm(request.POST, request.FILES, instance=obj)
        else:
            form = ModelForm(instance=obj)
        form.is_valid()

        values = {field.name: field.value() for field in form}
        errors = (
            {
                field: [
                    {"msg": next(iter(error)), "code": error.code} for error in _errors
                ]
                for field, _errors in form.errors.as_data().items()
            }
            if form.is_bound
            else {}
        )
        return {"values": values, "errors": errors}

    def get_extra_context(self, request, object_id):
        mode_choices = [EMPTY_FIELD_CHOICE] + list(PermissionModes.choices)
        token_auth_choices = [EMPTY_FIELD_CHOICE] + [
            (token.pk, str(token)) for token in TokenAuth.objects.all()
        ]
        object_type_choices = [EMPTY_FIELD_CHOICE] + [
            (object_type.pk, str(object_type))
            for object_type in ObjectType.objects.all()
        ]
        objecttypes_available = can_connect_to_objecttypes()
        data_field_choices = (
            self.get_data_field_choices() if objecttypes_available else {}
        )

        return {
            "object_fields": self.get_object_fields(),
            "data_field_choices": data_field_choices,
            "token_auth_choices": token_auth_choices,
            "object_type_choices": object_type_choices,
            "mode_choices": mode_choices,
            "form_data": self.get_form_data(request, object_id),
            "objecttypes_available": objecttypes_available,
        }

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_extra_context(request, object_id))

        if extra_context["objecttypes_available"] is False:
            msg = _(
                "ObjectTypes API is not reachable. Field-based authorization is impossible"
            )
            self.message_user(request, msg, messages.WARNING)

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_extra_context(request, object_id=None))

        if extra_context["objecttypes_available"] is False:
            msg = _(
                "ObjectTypes API is not reachable. Field-based authorization is impossible"
            )
            self.message_user(request, msg, messages.WARNING)

        return super().add_view(request, form_url, extra_context)


class PermissionInline(EditInlineAdminMixin, admin.TabularInline):
    model = Permission
    fk_name = "token_auth"
    fields = (
        "object_type",
        "mode",
        "use_fields",
        "fields",
        "get_uuid",
    )

    @admin.display(description="Object type UUID")
    def get_uuid(self, obj):
        return obj.object_type.uuid


@admin.register(TokenAuth)
class TokenAuthAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "contact_person",
        "organization",
        "administration",
        "application",
        "is_superuser",
    )
    readonly_fields = ("token",)
    inlines = [PermissionInline]
