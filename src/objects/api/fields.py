from rest_framework import serializers
from vng_api_common.serializers import CachedHyperlinkedIdentityField

from objects.core.models import ObjectRecord


class ObjectSlugRelatedField(serializers.SlugRelatedField):
    def get_queryset(self):
        queryset = ObjectRecord.objects.select_related(
            "object",
            "object__object_type",
            "correct",
            "corrected",
        ).order_by("-pk")

        record_instance = self.parent.parent.instance
        if not record_instance:
            return queryset.none()

        return queryset.filter(object=record_instance.object)


class ObjectUrlField(serializers.HyperlinkedIdentityField):
    lookup_field = "uuid"

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None

        lookup_value = getattr(obj.object, "uuid")
        kwargs = {self.lookup_url_kwarg: lookup_value}
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)


class CachedObjectUrlField(CachedHyperlinkedIdentityField):
    lookup_field = "uuid"

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, "pk") and obj.pk in (None, ""):
            return None
        return super().get_url(obj.object, view_name, request, format)
