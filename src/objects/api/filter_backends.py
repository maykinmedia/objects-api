from rest_framework.filters import OrderingFilter

from objects.utils.serializers import get_field_names_and_sources


class OrderingBackend(OrderingFilter):
    """
    This backend can be used when DB fields have different names/paths when
    serializer fields. It keeps mappings between serializer and DB fields and
    also supports ordering on nested fields.
    It also supports ordering on any attribute of JSON field
    """

    json_field = None

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
            valid_fields = [
                (name, source)
                for name, source in all_serializer_fields
                if source != "*"
            ]
        else:
            valid_fields = [
                (item, item) if isinstance(item, str) else item for item in valid_fields
            ]

        return valid_fields

    def remove_invalid_fields(self, queryset, fields, view, request):
        """add support for JSON fields"""
        valid_fields = [
            item[0]
            for item in self.get_valid_fields(queryset, view, {"request": request})
        ]

        def term_valid(term):
            if term.startswith("-"):
                term = term[1:]
            return term in valid_fields or (
                self.json_field and term.startswith(f"{self.json_field}__")
            )

        return [term for term in fields if term_valid(term)]

    def filter_queryset(self, request, queryset, view):
        # convert serializer fields to DB model ones
        db_ordering = self.get_db_ordering(request, queryset, view)

        if db_ordering:
            return queryset.order_by(*db_ordering)

        return queryset

    def get_db_ordering(self, request, queryset, view) -> list:
        """ get serializer ordering fields and convert them to db fields"""
        ordering = self.get_ordering(request, queryset, view)
        ordering = ordering or []

        valid_fields = dict(self.get_valid_fields(queryset, view, {"request": request}))

        db_ordering = []
        for order_field in ordering:
            prefix = "-" if order_field.startswith("-") else ""
            base = order_field if not order_field.startswith("-") else order_field[1:]

            if base in valid_fields:
                db_ordering.append(f"{prefix}{valid_fields[base]}")
            # json nested attribute
            elif (
                self.json_field
                and base.startswith(f"{self.json_field}__")
                and self.json_field in valid_fields
            ):
                nested_property = base[len(f"{self.json_field}") :]
                db_ordering.append(
                    f"{prefix}{valid_fields[self.json_field]}{nested_property}"
                )

        return db_ordering
