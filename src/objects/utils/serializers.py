import logging

from glom import GlomError, glom
from rest_framework import serializers

from objects.token.constants import PermissionModes

logger = logging.getLogger(__name__)


def build_spec(fields) -> dict:
    spec = {}
    for spec_field in fields:
        build_spec_field(spec, name=spec_field, value=spec_field)
    return spec


def build_spec_field(spec, name, value):
    if "__" in name:
        parent, field_name = name.split("__", 1)
        spec[parent] = spec.get(parent, {})
        build_spec_field(spec[parent], field_name, value)
    else:
        spec[name] = value.replace("__", ".")


def get_field_names(data: dict) -> list:
    field_names = []
    for key, value in data.items():
        if not isinstance(value, dict):
            field_names.append(key)
        else:
            field_names += [f"{key}__{val}" for val in get_field_names(value)]

    return field_names


class DynamicFieldsMixin:
    """
    this mixin allows selecting fields for serializer in the query param
    It also supports nested fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.not_allowed = set()

    def to_representation(self, instance):
        data = super().to_representation(instance)

        allowed_fields = self.get_allowed_fields(instance)
        query_fields = self.get_query_fields()

        if not query_fields and allowed_fields == ["*"]:
            return data

        #  limit all data to the allowed
        if allowed_fields == ["*"]:
            allowed_data = data
        else:
            spec_allowed = build_spec(allowed_fields)
            try:
                allowed_data = glom(data, spec_allowed)
            except GlomError as exc:
                raise serializers.ValidationError(
                    f"Fields in the configured authorization are absent in the data: {exc.args[0]}"
                )

        #  limit allowed data to requested in fields= query param
        if not query_fields:
            result_data = allowed_data
            not_allowed = set(get_field_names(data)) - set(get_field_names(result_data))
            self.not_allowed |= not_allowed
        else:
            spec_query = build_spec(query_fields)
            try:
                result_data = glom(allowed_data, spec_query)
            except GlomError as exc:
                raise serializers.ValidationError(
                    f"'fields' query parameter has invalid values: {exc.args[0]}"
                )
            not_allowed = set(get_field_names(glom(data, spec_query))) - set(
                get_field_names(result_data)
            )
            self.not_allowed |= not_allowed

        return result_data

    def get_query_fields(self) -> list:
        request = self.context.get("request")
        if not request:
            return []

        fields = request.query_params.get("fields")
        if not fields:
            return []

        return list(set(field.strip() for field in fields.split(",")))

    def get_allowed_fields(self, instance) -> list:
        request = self.context.get("request")

        # if not instance -> create or update -> all fields are allowed
        if not request:
            return ["*"]

        permission = request.auth.get_permission_for_object_type(instance.object_type)
        if permission.mode == PermissionModes.read_only and permission.use_fields:
            return permission.fields

        return ["*"]
