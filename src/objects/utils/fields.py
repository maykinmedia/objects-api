from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


@extend_schema_field({"type": "object", "additionalProperties": True})
class JSONObjectField(serializers.JSONField):
    """
    serializers.JSONField does not have a type by default and will show `any` in api spec.
    """
