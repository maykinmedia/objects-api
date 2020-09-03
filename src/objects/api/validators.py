import jsonschema
import requests
from rest_framework import serializers


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

        if not data:
            return

        response = requests.get(object_type)
        try:
            response.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise serializers.ValidationError(exc.args[0]) from exc

        type_data = response.json()
        versions = list(
            filter(lambda x: x.get("version") == version, type_data.get("versions", []))
        )
        try:
            version_data = versions[0]
        except IndexError:
            msg = f"{object_type} doesn't include JSON schema for version {version}"
            raise serializers.ValidationError(msg)

        schema = version_data["jsonSchema"]
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as exc:
            raise serializers.ValidationError(exc.args[0], code=self.code) from exc
