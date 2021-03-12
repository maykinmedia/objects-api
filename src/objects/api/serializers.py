from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField

from objects.core.models import Object, ObjectRecord, ObjectType

from .validators import IsImmutableValidator, JsonSchemaValidator


class ObjectSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        queryset = ObjectRecord.objects.all()

        object_instance = self.parent.parent.instance
        if not object_instance:
            return queryset.none()

        return queryset.filter(object=object_instance)


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


class ObjectTypeField(serializers.RelatedField):
    default_error_messages = {
        "does_not_exist": _("ObjectType with url={value} is not configured."),
        "invalid": _("Invalid value."),
    }

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_by_url(data)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", value=smart_text(data))
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        return obj.url


class ObjectSerializer(serializers.HyperlinkedModelSerializer):
    type = ObjectTypeField(
        source="object_type",
        queryset=ObjectType.objects.all(),
        help_text=_("Url reference to OBJECTTYPE in Objecttypes API"),
        validators=[IsImmutableValidator()],
    )
    record = ObjectRecordSerializer(
        source="current_record", help_text=_("State of the OBJECT at a certain time")
    )

    class Meta:
        model = Object
        fields = ("url", "uuid", "type", "record")
        extra_kwargs = {
            "url": {"lookup_field": "uuid"},
            "uuid": {"validators": [IsImmutableValidator()]},
        }
        validators = [JsonSchemaValidator()]

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        actual_date = self.context["request"].query_params.get("date", None)
        registration_date = self.context["request"].query_params.get(
            "registrationDate", None
        )

        if not actual_date and not registration_date:
            return ret

        record = (
            instance.get_actual_record(actual_date)
            if actual_date
            else instance.get_registration_record(registration_date)
        )
        ret["record"] = self.fields["record"].to_representation(record)
        return ret

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


class GeoWithinSerializer(serializers.Serializer):
    within = GeometryField(required=False)


class ObjectSearchSerializer(serializers.Serializer):
    geometry = GeoWithinSerializer(required=True)
