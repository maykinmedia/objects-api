from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class DynamicFieldsMixin:
    """
    this mixin allows selecting fields for serializer in the query param
    It also supports nested fields which are serializers themselves.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        query_fields = self.get_query_fields()
        if not query_fields:
            return

        # support selecting nested fields
        nested_fields = [
            field_name
            for field_name, field in self.fields.items()
            if isinstance(field, serializers.Serializer)
        ]
        for nested_field in nested_fields:
            allowed_nested_fields = self.update_fields(query_fields, nested_field)
            if allowed_nested_fields:
                query_fields -= allowed_nested_fields
                query_fields |= {nested_field}

        self.update_fields(query_fields)

    def update_fields(self, query_fields, parent=None) -> set:
        pattern = f"{parent}__" if parent else ""
        allowed = set(
            field_name.replace(pattern, "", 1)
            for field_name in query_fields
            if field_name.startswith(pattern)
        )
        fields = self.fields[parent].fields if parent else self.fields
        existing = set(fields)

        extra_fields = allowed - existing
        if extra_fields:
            msg_fields = [f"{pattern}{field_name}" for field_name in extra_fields]
            raise serializers.ValidationError(
                _("'fields' query parameter has invalid values: %(msg_fields)s")
                % {"msg_fields": ", ".join(msg_fields)}
            )

        for field_name in existing - allowed:
            fields.pop(field_name)

        # add back prefix
        return set(f"{pattern}{field_name}" for field_name in allowed)

    def get_query_fields(self) -> set:
        request = self.context.get("request")
        if not request:
            return set()

        if request.method != "GET":
            return set()

        fields = request.query_params.get("fields")
        if not fields:
            return set()

        return set(field.strip() for field in fields.split(","))
