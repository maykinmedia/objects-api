from rest_framework.filters import OrderingFilter
from vng_api_common.filters import Backend

from objects.utils.serializers import get_field_names


class ObjectFilterBackend(Backend):
    def filter_queryset(self, request, queryset, view):
        # TODO put logic here
        pass


class OrderingBackend(OrderingFilter):
    def get_valid_fields(self, queryset, view, context={}):
        """ add nested fields to available fields for ordering"""
        valid_fields = getattr(view, "ordering_fields", self.ordering_fields)

        if valid_fields is None:
            # Default to allowing filtering on serializer fields
            return self.get_default_valid_fields(queryset, view, context)

        elif valid_fields == "__all__":
            # View explicitly allows filtering on any model field
            serializer = view.get_serializer()
            all_serializer_fields = get_field_names(serializer.fields)

            # FIXME add JSON fields
            all_fields = all_serializer_fields

            valid_fields = [
                (
                    item.replace("record__", "records__"),
                    item.replace("record__", "records__"),
                )
                for item in all_fields
            ]
        else:
            valid_fields = [
                (item, item) if isinstance(item, str) else item for item in valid_fields
            ]

        return valid_fields
