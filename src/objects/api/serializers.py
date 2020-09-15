from django.db import transaction

from rest_framework import serializers

from objects.core.models import Object, ObjectRecord

from .validators import CorrectionValidator, JsonSchemaValidator


class ObjectRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectRecord
        fields = (
            "typeVersion",
            "data",
            "startDate",
            "endDate",
            "registrationDate",
            "correct",
        )
        extra_kwargs = {
            "typeVersion": {"source": "version"},
            "startDate": {"source": "start_date"},
            "endDate": {"source": "end_date", "read_only": True},
            "registrationDate": {"source": "registration_date", "read_only": True},
            "correct": {"required": False},
        }


class HistoryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectRecord
        fields = (
            "id",
            "typeVersion",
            "data",
            "startDate",
            "endDate",
            "registrationDate",
            "corrected",
        )
        extra_kwargs = {
            "id": {"read_only": True},
            "typeVersion": {"source": "version"},
            "startDate": {"source": "start_date"},
            "endDate": {"source": "end_date", "read_only": True},
            "registrationDate": {"source": "registration_date", "read_only": True},
            "corrected": {"read_only": True},
        }


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    record = ObjectRecordSerializer(source="current_record")

    class Meta:
        model = Object
        fields = ("url", "type", "record")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "type": {"source": "object_type"},
        }
        validators = [JsonSchemaValidator(), CorrectionValidator()]

    @transaction.atomic
    def create(self, validated_data):
        record_data = validated_data.pop("current_record")
        object = super().create(validated_data)

        record_data["object"] = object
        ObjectRecordSerializer().create(record_data)
        return object

    @transaction.atomic
    def update(self, instance, validated_data):
        record_data = validated_data.pop("current_record", None)
        object = super().update(instance, validated_data)

        if record_data:
            record_data["object"] = object
            # in case of PATCH:
            if not record_data.get("version"):
                record_data["version"] = object.current_record.version
            ObjectRecordSerializer().create(record_data)
        return object
