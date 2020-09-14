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
        #  don't check if type and version are not changed
        if not attrs.get("object_type") and not attrs.get("version"):
            return

        object_type = attrs.get("object_type") or self.instance.object_type
        version = attrs.get("version") or self.instance.version
        if attrs.get("current_record"):
            data = attrs["current_record"].get("data", {})
        else:
            data = self.instance.last_record.data

        try:
            check_objecttype(object_type, version, data)
        except ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc


class CorrectionValidator:
    message = "Only records of the same objects can be corrected"
    code = "invalid-correction"

    def set_context(self, serializer):
        """
        This hook is called by the serializer instance,
        prior to the validation call being made.
        """
        self.instance = getattr(serializer, "instance", None)

    def __call__(self, attrs):
        record = attrs.get("current_record", {})
        correct = record.get("correct")

        if correct and correct.object != self.instance:
            raise serializers.ValidationError(self.message, code=self.code)
