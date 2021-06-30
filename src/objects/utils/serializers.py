from django.utils.translation import ugettext_lazy as _

from glom import GlomError, glom
from rest_framework import serializers


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


class DynamicFieldsMixin:
    """
    this mixin allows selecting fields for serializer in the query param
    It also supports nested fields which are serializers themselves.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)

        query_fields = self.get_query_fields()

        if not query_fields:
            return data

        spec = build_spec(query_fields)
        try:
            return glom(data, spec)
        except GlomError as exc:
            raise serializers.ValidationError(
                f"'fields' query parameter has invalid values: {exc.args[0]}"
            )

    def get_query_fields(self) -> set:
        request = self.context.get("request")
        if not request or request.method != "GET":
            return set()

        fields = request.query_params.get("fields")
        if not fields:
            return set()

        return set(field.strip() for field in fields.split(","))
