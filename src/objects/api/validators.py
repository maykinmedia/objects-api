from django.core.exceptions import ValidationError

from rest_framework import serializers

from objects.core.utils import check_objecttype


class JsonSchemaValidator:
    code = "invalid-json-schema"

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs):
        object_type = attrs.get("object_type", self.instance.object_type)
        version = attrs.get("version", self.instance.version)
        data = attrs.get("data", {})

        try:
            check_objecttype(object_type, version, data)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc
