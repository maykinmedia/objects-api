from django.db import transaction
from django.utils.translation import gettext_lazy as _

import structlog
from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField

from objects.core.models import Object, ObjectRecord, ObjectType
from objects.token.models import Permission, TokenAuth
from objects.utils.serializers import DynamicFieldsMixin

from .fields import CachedObjectUrlField, ObjectSlugRelatedField, ObjectTypeField
from .utils import merge_patch
from .validators import GeometryValidator, IsImmutableValidator, JsonSchemaValidator

logger = structlog.stdlib.get_logger(__name__)


class ObjectRecordSerializer(serializers.ModelSerializer):
    correctionFor = ObjectSlugRelatedField(
        source="correct",
        slug_field="index",
        required=False,
        allow_null=True,
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
    url = CachedObjectUrlField(view_name="object-detail")
    uuid = serializers.UUIDField(
        source="object.uuid",
        required=False,
        validators=[IsImmutableValidator()],
        help_text=_("Unique identifier (UUID4)"),
    )
    type = ObjectTypeField(
        min_length=1,
        max_length=1000,
        source="object.object_type",
        queryset=ObjectType.objects.all(),
        help_text=_("Url reference to OBJECTTYPE in Objecttypes API"),
        validators=[IsImmutableValidator()],
    )
    record = ObjectRecordSerializer(
        source="*", help_text=_("State of the OBJECT at a certain time")
    )

    class Meta:
        model = ObjectRecord
        fields = ("url", "uuid", "type", "record")
        extra_kwargs = {
            "url": {"lookup_field": "object.uuid"},
        }
        validators = [JsonSchemaValidator(), GeometryValidator()]

    @transaction.atomic
    def create(self, validated_data):
        object_data = validated_data.pop("object")
        object = Object.objects.create(**object_data)

        validated_data["object"] = object
        record = super().create(validated_data)
        token_auth: TokenAuth = self.context["request"].auth
        logger.info(
            "object_created",
            object_uuid=str(object.uuid),
            objecttype_uuid=str(object.object_type.uuid),
            objecttype_version=record.version,
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )
        return record

    @transaction.atomic
    def update(self, instance, validated_data):
        # object_data is not used since all object attributes are immutable
        validated_data.pop("object", None)
        validated_data["object"] = instance.object
        # version should be set
        if "version" not in validated_data:
            validated_data["version"] = instance.version
        # start_at should be set
        if "start_at" not in validated_data:
            validated_data["start_at"] = instance.start_at

        if self.partial and "data" in validated_data:
            # Apply JSON Merge Patch for record data
            validated_data["data"] = merge_patch(instance.data, validated_data["data"])

        record = super().create(validated_data)
        token_auth: TokenAuth = self.context["request"].auth
        logger.info(
            "object_updated",
            object_uuid=str(record.object.uuid),
            objecttype_uuid=str(record.object.object_type.uuid),
            objecttype_version=record.version,
            token_identifier=token_auth.identifier,
            token_application=token_auth.application,
        )
        return record


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
