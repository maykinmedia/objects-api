from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from objects.core.models import ObjectRecord


class ObjectSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        queryset = ObjectRecord.objects.all()

        object_instance = self.parent.parent.instance
        if not object_instance:
            return queryset.none()

        return queryset.filter(object=object_instance)


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
