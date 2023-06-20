from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_filters import filters
from vng_api_common.filters import URLModelChoiceFilter


class ObjectTypeField(filters.ModelChoiceField):
    default_error_messages = {
        "max_length": _("The value has too many characters"),
        "min_length": _("The value has too few characters"),
        "invalid_choice": _(
            "Select a valid object type. %(value)s is not one of the"
            " available choices."
        ),
        "invalid": _("Invalid value."),
    }

    def __init__(self, *args, **kwargs):
        self.max_length = kwargs.pop("max_length", None)
        self.min_length = kwargs.pop("min_length", None)

        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if value in self.empty_values:
            return None

        if self.max_length and len(value) > self.max_length:
            raise ValidationError(self.error_messages["max_length"], code="max_length")

        if self.min_length and len(value) < self.min_length:
            raise ValidationError(self.error_messages["min_length"], code="min_length")

        try:
            result = self.queryset.get_by_url(value)
        except self.queryset.model.DoesNotExist:
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        return result


class ObjectTypeFilter(URLModelChoiceFilter):
    field_class = ObjectTypeField
