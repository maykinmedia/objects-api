from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from objects.core.models import ObjectRecord


class ObjectSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        queryset = ObjectRecord.objects.all()

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
            self.fail("does_not_exist", value=smart_text(data))
        except (TypeError, ValueError):
            self.fail("invalid")

    def to_representation(self, obj):
        return obj.url
