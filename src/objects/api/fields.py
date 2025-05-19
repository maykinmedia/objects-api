from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from vng_api_common.utils import get_uuid_from_path
from zgw_consumers.models import Service

from objects.core.models import ObjectRecord


class ObjectSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        queryset = ObjectRecord.objects.select_related(
            "object",
            "object__object_type",
            "object__object_type__service",
            "correct",
            "corrected",
        ).order_by("-pk")

        record_instance = self.parent.parent.instance
        if not record_instance:
            return queryset.none()

        return queryset.filter(object=record_instance.object)


class ObjectTypeField(serializers.RelatedField):
    default_error_messages = {
        "max_length": _("The value has too many characters"),
        "min_length": _("The value has too few characters"),
        "does_not_exist": _("ObjectType with url={value} is not configured."),
        "invalid": _("Invalid value."),
    }

    def __init__(self, **kwargs):
        self.max_length = kwargs.pop("max_length", None)
        self.min_length = kwargs.pop("min_length", None)

        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if self.max_length and len(data) > self.max_length:
            self.fail("max_length")

        if self.min_length and len(data) < self.min_length:
            self.fail("min_length")

        try:
            return self.get_queryset().get_by_url(data)
        except ObjectDoesNotExist:
            # if service is configured, but object_type is missing
            # let's try to create an ObjectType
            service = Service.get_service(data)
            if not service:
                self.fail("does_not_exist", value=smart_str(data))

            uuid = get_uuid_from_path(data)
            object_type = self.get_queryset().model(service=service, uuid=uuid)

            try:
                object_type.clean()
            except ValidationError:
                self.fail("does_not_exist", value=smart_str(data))

            object_type.save()
            return object_type

        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        return obj.url


class ObjectUrlField(serializers.HyperlinkedIdentityField):
    lookup_field = "uuid"

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        lookup_value = getattr(obj.object, "uuid")
        kwargs = {self.lookup_url_kwarg: lookup_value}
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
