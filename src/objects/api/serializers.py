from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField

from objects.core.models import Object, ObjectRecord, ObjectType
from objects.token.models import Permission
from objects.utils.serializers import DynamicFieldsMixin

from .fields import ObjectSlugRelatedField, ObjectTypeField
from .validators import IsImmutableValidator, JsonSchemaValidator


class ObjectRecordSerializer(serializers.ModelSerializer):
    correctionFor = ObjectSlugRelatedField(
        source="correct",
        slug_field="index",
        required=False,
        help_text=_("Index of the record corrected by the current record"),
    )
    correctedBy = serializers.SlugRelatedField(
        source="corrected",
        slug_field="index",
        read_only=True,
        help_text=_("Index of the record, which corrects the current record"),
    )

    class Meta:
        model = ObjectRecord
        fields = (
            "index",
            "typeVersion",
            "data",
            "geometry",
            "startAt",
            "endAt",
            "registrationAt",
            "correctionFor",
            "correctedBy",
        )
        extra_kwargs = {
            "index": {"read_only": True},
            "typeVersion": {"source": "version"},
            "startAt": {"source": "start_at"},
            "endAt": {"source": "end_at", "read_only": True},
            "registrationAt": {"source": "registration_at", "read_only": True},
        }


class HistoryRecordSerializer(serializers.ModelSerializer):
    correctionFor = serializers.SlugRelatedField(
        source="correct",
        slug_field="index",
        read_only=True,
        help_text=_("Index of the record corrected by the current record"),
    )
    correctedBy = serializers.SlugRelatedField(
        source="corrected",
        slug_field="index",
        read_only=True,
        help_text=_("Index of the record, which corrects the current record"),
    )

    class Meta:
        model = ObjectRecord
        fields = (
            "index",
            "typeVersion",
            "data",
            "geometry",
            "startAt",
            "endAt",
            "registrationAt",
            "correctionFor",
            "correctedBy",
        )
        extra_kwargs = {
            "index": {"read_only": True},
            "typeVersion": {"source": "version"},
            "startAt": {"source": "start_at"},
            "endAt": {"source": "end_at", "read_only": True},
            "registrationAt": {"source": "registration_at", "read_only": True},
        }


class ObjectSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    type = ObjectTypeField(
        min_length=1,
        max_length=1000,
        source="object_type",
        queryset=ObjectType.objects.all(),
        help_text=_("Url reference to OBJECTTYPE in Objecttypes API"),
        validators=[IsImmutableValidator()],
    )
    record = ObjectRecordSerializer(
        help_text=_("State of the OBJECT at a certain time")
    )

    class Meta:
        model = Object
        fields = ("url", "uuid", "type", "record")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "uuid": {"validators": [IsImmutableValidator()]},
        }
        validators = [JsonSchemaValidator()]

    @transaction.atomic
    def create(self, validated_data):
        record_data = validated_data.pop("record")
        object = super().create(validated_data)

        record_data["object"] = object
        ObjectRecordSerializer().create(record_data)
        return object

    @transaction.atomic
    def update(self, instance, validated_data):
        record_data = validated_data.pop("record", None)
        object = super().update(instance, validated_data)

        if record_data:
            record_data["object"] = object
            # in case of PATCH:
            if not record_data.get("version"):
                record_data["version"] = object.record.version
            ObjectRecordSerializer().create(record_data)
        return object


class GeoWithinSerializer(serializers.Serializer):
    within = GeometryField(required=False)


class ObjectSearchSerializer(serializers.Serializer):
    geometry = GeoWithinSerializer(required=False)


class PermissionSerializer(serializers.ModelSerializer):
    type = ObjectTypeField(
        min_length=1,
        max_length=1000,
        source="object_type",
        queryset=ObjectType.objects.all(),
        help_text=_("Url reference to OBJECTTYPE in Objecttypes API"),
    )

    class Meta:
        model = Permission
        fields = ("type", "mode", "use_fields", "fields")
