from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import requests
from rest_framework import serializers
from rest_framework.fields import get_attribute
from zgw_consumers.client import build_client

from objects.core.utils import check_objecttype

from .constants import Operators
from .utils import merge_patch, string_to_value


class JsonSchemaValidator:
    code = "invalid-json-schema"
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = getattr(serializer, "instance", None)

        # create
        if not instance:
            object_type = attrs.get("object", {}).get("object_type")
            version = attrs.get("version")
            data = attrs.get("data", {})

        # update
        else:
            object_type = (
                attrs.get("object", {}).get("object_type")
                if "object" in attrs
                else instance.object.object_type
            )
            version = attrs.get("version") if "version" in attrs else instance.version
            data = attrs.get("data", {}) if "data" in attrs else instance.data
            if serializer.partial and "data" in attrs:
                # Apply JSON Merge Patch for record data
                data = merge_patch(instance.data, attrs["data"])

        if not object_type or not version:
            return

        try:
            check_objecttype(object_type, version, data)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc


class IsImmutableValidator:
    """
    Validate that the field should not be changed in update action
    """

    message = _("This field can't be changed")
    code = "immutable-field"
    requires_context = True

    def __call__(self, new_value, serializer_field):
        instance = getattr(serializer_field.parent, "instance", None)
        # no instance -> it's not an update
        if not instance:
            return

        current_value = get_attribute(instance, serializer_field.source_attrs)

        if new_value != current_value:
            raise serializers.ValidationError(self.message, code=self.code)


def validate_data_attr_value_part(value_part: str, code: str):
    try:
        variable, operator, val = value_part.rsplit("__", 2)
    except ValueError:
        message = _(
            "Filter expression '%(value_part)s' doesn't have the shape 'key__operator__value'"
        ) % {"value_part": value_part}
        raise serializers.ValidationError(message, code=code)

    if operator not in Operators.values:
        message = _("Comparison operator `%(operator)s` is unknown") % {
            "operator": operator
        }
        raise serializers.ValidationError(message, code=code)

    if operator not in (
        Operators.exact,
        Operators.icontains,
        Operators.in_list,
    ) and isinstance(string_to_value(val), str):
        message = _(
            "Operator `%(operator)s` supports only dates and/or numeric values"
        ) % {"operator": operator}
        raise serializers.ValidationError(message, code=code)


def validate_data_attrs(value: str):
    # todo remove when 'data_attrs' filter is removed
    code = "invalid-data-attrs-query"
    parts = value.split(",")

    for value_part in parts:
        validate_data_attr_value_part(value_part, code)


def validate_data_attr(value: list):
    code = "invalid-data-attr-query"

    for value_part in value:
        # check that comma can be only in the value part
        if "," in value_part.rsplit("__", 1)[0]:
            message = _(
                "Filter expression '%(value_part)s' doesn't have the shape 'key__operator__value'"
            ) % {"value_part": value_part}
            raise serializers.ValidationError(message, code=code)

        validate_data_attr_value_part(value_part, code)


class GeometryValidator:
    code = "geometry-not-allowed"
    message = _("This object type doesn't support geometry")
    requires_context = True

    def __call__(self, attrs, serializer):
        instance = getattr(serializer, "instance", None)
        object_type = (
            attrs.get("object", {}).get("object_type") or instance.object.object_type
        )
        geometry = attrs.get("geometry")

        if not geometry:
            return

        client = build_client(object_type.service)
        try:
            response = client.get(url=object_type.url)
        except requests.RequestException as exc:
            msg = f"Object type can not be retrieved: {exc.args[0]}"
            raise ValidationError(msg)

        allow_geometry = response.json().get("allowGeometry", True)

        if geometry and not allow_geometry:
            raise serializers.ValidationError(self.message, code=self.code)
