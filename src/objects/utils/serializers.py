import logging
from collections import defaultdict

from glom import GlomError, glom
from rest_framework import serializers

from objects.token.constants import PermissionModes

logger = logging.getLogger(__name__)


ALL_FIELDS = ["*"]


def build_spec(fields, sep=".") -> dict:
    spec = {}
    for spec_field in fields:
        build_spec_field(spec, name=spec_field, value=spec_field, sep=sep)
    return spec


def build_spec_field(spec, name, value, sep):
    if "__" in name:
        parent, field_name = name.split("__", 1)
        spec[parent] = spec.get(parent, {})
        build_spec_field(spec[parent], field_name, value, sep)
    else:
        spec[name] = value.replace("__", sep)


def get_field_names(data: dict) -> list:
    field_names = []
    for key, value in data.items():
        if isinstance(value, dict):
            field_names += [f"{key}__{val}" for val in get_field_names(value)]
        elif isinstance(value, serializers.Serializer):
            field_names += [f"{key}__{val}" for val in get_field_names(value.fields)]
        else:
            field_names.append(key)

    return field_names


class NotAllowedDict(defaultdict):
    def pretty(self):
        if len(self.keys()) == 0:
            return ""
        if len(self.keys()) == 1:
            value = list(self.values())[0]
            return ",".join(value)
        return "; ".join([f"{key}={','.join(value)}" for (key, value) in self.items()])


class DynamicFieldsMixin:
    """
    this mixin allows selecting fields for serializer in the query param
    It also supports nested fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.not_allowed = NotAllowedDict(set)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        allowed_fields = self.get_allowed_fields(instance)
        query_fields = self.get_query_fields()

        if not query_fields and allowed_fields == ALL_FIELDS:
            return data

        #  limit all data to the allowed
        if allowed_fields == ALL_FIELDS:
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
            if not_allowed:
                self.not_allowed[
                    f"{instance.object_type.url}({instance.record.version})"
                ] |= not_allowed
        else:
            spec_query = build_spec(query_fields)
            try:
                result_data = glom(allowed_data, spec_query)
            except GlomError as exc:
                raise serializers.ValidationError(
                    f"'fields' query parameter has invalid or unauthorized values: {exc.args[0]}"
                )
            not_allowed = set(get_field_names(glom(data, spec_query))) - set(
                get_field_names(result_data)
            )
            if not_allowed:
                self.not_allowed[
                    f"{instance.object_type.url}({instance.record.version})"
                ] |= not_allowed

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
            return ALL_FIELDS

        # use prefetch_related for DB optimization
        if getattr(instance.object_type, "token_permissions", None):
            permission = instance.object_type.token_permissions[0]
        else:
            permission = request.auth.get_permission_for_object_type(
                instance.object_type
            )
        if permission.mode == PermissionModes.read_only and permission.use_fields:
            return permission.fields.get(str(instance.record.version), [])

        return ALL_FIELDS
