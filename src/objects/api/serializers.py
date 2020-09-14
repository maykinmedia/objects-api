from django.db import transaction

from rest_framework import serializers

from objects.core.models import Object, ObjectRecord

from .validators import CorrectRecordValidator, JsonSchemaValidator


class ObjectRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectRecord
        fields = ("data", "start_date", "end_date", "registration_date", "correct")
        extra_kwargs = {
            "end_date": {"read_only": True},
            "publication_date": {"read_only": True},
            "correct": {"validators": [CorrectRecordValidator()]},
        }


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

    def validate(self, attrs):
        valid_attrs = super().validate(attrs)

        return valid_attrs

    @transaction.atomic
    def create(self, validated_data):
        record_data = validated_data.pop("current_record")
        object = super().create(validated_data)

        record_data["object"] = object
        ObjectRecordSerializer().create(record_data)
        return object

    @transaction.atomic
    def update(self, instance, validated_data):
        record_data = validated_data.pop("current_record")
        object = super().update(instance, validated_data)

        record_data["object"] = object
        ObjectRecordSerializer().create(record_data)
        return object
