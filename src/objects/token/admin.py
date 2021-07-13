from django.contrib import admin

from objects.api.serializers import ObjectSerializer
from objects.core.models import ObjectType
from objects.utils.admin import EditInlineAdminMixin
from objects.utils.serializers import build_spec, get_field_names

from .models import Permission, TokenAuth


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("token_auth", "object_type", "mode", "use_fields")

    def get_object_fields(self):
        object_serializer = ObjectSerializer()
        object_fields = build_spec(get_field_names(object_serializer.fields), sep="__")
        return object_fields

    def get_data_fields(self):
        data_fields = {}
        for object_type in ObjectType.objects.all():
            client = object_type.service.build_client()
            url = f"{object_type.url}/versions"
            response = client.request(url, "objectversion_list")
            if isinstance(response, dict):
                response = response["results"]

            # to select fields use the latest version
            # TODO should we include objecttype versions in field-based auth?
            schema = response[-1]["jsonSchema"]
            # use only first level of properties
            properties = list(schema["properties"].keys())
            data_fields[object_type.id] = properties
        return data_fields

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["object_fields"] = self.get_object_fields()
        extra_context["data_fields"] = self.get_data_fields()

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )


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
