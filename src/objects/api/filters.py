from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django_filters import filters
from rest_framework import serializers
from vng_api_common.filters import URLModelChoiceFilter
from vng_api_common.filtersets import FilterSet

from objects.core.models import Object, ObjectType

from .constants import Operators
from .utils import display_choice_values_for_help_text, string_to_value
from .validators import validate_data_attrs


class ObjectFilterForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        registration_date = cleaned_data.get("registrationDate")

        if date and registration_date:
            raise serializers.ValidationError(
                _(
                    "'date' and 'registrationDate' parameters can't be used in the same request"
                ),
                code="invalid-date-query-params",
            )

        return cleaned_data


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


class ObjectFilterSet(FilterSet):
    type = ObjectTypeFilter(
        field_name="object_type",
        help_text=_("Url reference to OBJECTTYPE in Objecttypes API"),
        queryset=ObjectType.objects.all(),
        min_length=1,
        max_length=1000,
    )
    date = filters.DateFilter(
        method="filter_date",
        help_text=_(
            "Display record data for the specified material date, i.e. the specified "
            "date would be between `startAt` and `endAt` attributes. The default value is today"
        ),
    )
    registrationDate = filters.DateFilter(
        method="filter_registration_date",
        help_text=_(
            "Display record data for the specified registration date, i.e. the specified "
            "date would be between `registrationAt` attributes of different records"
        ),
    )
    data_attrs = filters.CharFilter(
        method="filter_data_attrs",
        validators=[validate_data_attrs],
        help_text=_(
            """Only include objects that have attributes with certain values.
Data filtering expressions are comma-separated and are structured as follows:
A valid parameter value has the form `key__operator__value`.
`key` is the attribute name, `operator` is the comparison operator to be used and `value` is the attribute value.
Note: Values can be string, numeric, or dates (ISO format; YYYY-MM-DD).

Valid operator values are:
%(operator_choices)s
`value` may not contain double underscore or comma characters.
`key` may not contain comma characters and includes double underscore only if it indicates nested attributes.

Example: in order to display only objects with `height` equal to 100, query `data_attrs=height__exact__100`
should be used. If `height` is nested inside `dimensions` attribute, query should look like
`data_attrs=dimensions__height__exact__100`
"""
        )
        % {"operator_choices": display_choice_values_for_help_text(Operators)},
    )

    class Meta:
        model = Object
        fields = ("type", "data_attrs", "date", "registrationDate")
        form = ObjectFilterForm

    def filter_data_attrs(self, queryset, name, value: str):
        parts = value.split(",")

        for value_part in parts:
            variable, operator, val = value_part.rsplit("__", 2)
            real_value = string_to_value(val)

            if operator == "exact":
                #  for exact operator try to filter on string and numeric values
                in_vals = [val]
                if real_value != value:
                    in_vals.append(real_value)
                queryset = queryset.filter(
                    **{f"records__data__{variable}__in": in_vals}
                )

            else:
                queryset = queryset.filter(
                    **{f"records__data__{variable}__{operator}": real_value}
                )

        return queryset

    def filter_date(self, queryset, name, value: date):
        return queryset.filter_for_date(value)

    def filter_registration_date(self, queryset, name, value: date):
        return queryset.filter_for_registration_date(value)
