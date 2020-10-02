from django_filters import filters
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_help_text

from objects.core.models import Object


class ObjectFilterSet(FilterSet):
    type = filters.CharFilter(
        field_name="object_type", help_text=get_help_text("core.Object", "object_type")
    )

    class Meta:
        model = Object
        fields = ("type",)
