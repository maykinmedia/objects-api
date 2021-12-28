from rest_framework.filters import OrderingFilter

from objects.utils.serializers import get_field_names_and_sources


class OrderingBackend(OrderingFilter):
    """
    This backend can be used when DB fields have different names/paths when
    serializer fields. It keeps mappings between serializer and DB fields and
    also supports ordering on nested fields.
    """

    def get_valid_fields(self, queryset, view, context={}):
        """ add nested fields to available fields for ordering"""
        valid_fields = getattr(view, "ordering_fields", self.ordering_fields)

        if valid_fields is None:
            # Default to allowing filtering on serializer fields
            return self.get_default_valid_fields(queryset, view, context)

        elif valid_fields == "__all__":
            # View explicitly allows filtering on any model field
            serializer = view.get_serializer()
            all_serializer_fields = get_field_names_and_sources(serializer.fields)

            # FIXME add JSON fields
            all_fields = all_serializer_fields
            valid_fields = [
                (name, source) for name, source in all_fields if source != "*"
            ]
        else:
            valid_fields = [
                (item, item) if isinstance(item, str) else item for item in valid_fields
            ]

        return valid_fields

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        ordering = ordering or []

        # convert serializer fields to DB model ones
        valid_fields = dict(self.get_valid_fields(queryset, view, {"request": request}))
        db_ordering = [
            "-" + valid_fields[field[1:]]
            if field.startswith("-")
            else valid_fields[field]
            for field in ordering
        ]

        if db_ordering:
            return queryset.order_by(*db_ordering)

        return queryset
