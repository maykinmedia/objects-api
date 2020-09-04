from rest_framework import serializers

from objects.core.models import Object, ObjectRecord

from .validators import JsonSchemaValidator


class ObjectRecordSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("data", "start_date", "end_date", "registration_date")
        model = ObjectRecord


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    record = ObjectRecordSerializer(source="current_record")

    class Meta:
        model = Object
        fields = ("url", "type", "version", "record")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "type": {"source": "object_type"},
        }
        validators = [JsonSchemaValidator()]
