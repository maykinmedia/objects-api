import jsonschema
import requests
from rest_framework import serializers

from .models import Object


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Object
        fields = ("url", "type", "version", "data")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "type": {"source": "object_type"},
        }

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)

        # validate object data based on objecttype schema
        type = validated_attrs["object_type"]
        version = validated_attrs["version"]
        data = validated_attrs["data"]

        response = requests.get(type)
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
            msg = f"{type} doesn't include JSON schema for version {version}"
            raise serializers.ValidationError(msg)

        schema = version_data["jsonSchema"]
        try:
            jsonschema.validate(data, schema)
        except jsonschema.exceptions.ValidationError as exc:
            raise serializers.ValidationError(exc.args[0]) from exc

        return validated_attrs
