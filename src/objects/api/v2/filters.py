from datetime import date as date_

from django import forms
from django.utils.translation import gettext_lazy as _

from django_filters import filters
from rest_framework import serializers
from vng_api_common.filtersets import FilterSet

from objects.core.models import ObjectRecord, ObjectType
from objects.utils.filters import ObjectTypeFilter

from ..constants import Operators
from ..utils import display_choice_values_for_help_text, string_to_value
from ..validators import validate_data_attrs


class ObjectRecordFilterForm(forms.Form):
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


class ObjectRecordFilterSet(FilterSet):
    type = ObjectTypeFilter(
        field_name="object__object_type",
        help_text=_("Url reference to OBJECTTYPE in Objecttypes API"),
        queryset=ObjectType.objects.all(),
        min_length=1,
        max_length=1000,
    )
    typeVersion = filters.NumberFilter(
        field_name="version",
        help_text=_("Display record data for the specified type version"),
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
    data_icontains = filters.CharFilter(
        method="filter_data_icontains",
        help_text=_("Search in all `data` values of string properties."),
    )

    class Meta:
        model = ObjectRecord
        fields = ("type", "data_attrs", "date", "registrationDate")
        form = ObjectRecordFilterForm

    def filter_data_attrs(self, queryset, name, value: str):
        parts = value.split(",")

        for value_part in parts:
            variable, operator, str_value = value_part.rsplit("__", 2)
            real_value = string_to_value(str_value)

            if operator == "exact":
                #  for exact operator try to filter on string and numeric values
                in_vals = [str_value]
                if real_value != value:
                    in_vals.append(real_value)
                queryset = queryset.filter(**{f"data__{variable}__in": in_vals})
            elif operator == "icontains":
                # icontains treats everything like strings
                queryset = queryset.filter(
                    **{f"data__{variable}__icontains": str_value}
                )

            else:
                # gt, gte, lt, lte operators
                queryset = queryset.filter(
                    **{f"data__{variable}__{operator}": real_value}
                )

        return queryset

    def filter_data_icontains(self, queryset, name, value: str):
        # WHERE clause has jsonpath: where data @? '$.** ? (@ like_regex "$value" flag "i")'
        where_str = "core_objectrecord.data @? CONCAT('$.** ? (@ like_regex \"',%s::text,'\" flag \"i\")')::jsonpath"
        return queryset.extra(where=[where_str], params=[value])

    def filter_date(self, queryset, name, value: date_):
        return queryset.filter_for_date(value)

    def filter_registration_date(self, queryset, name, value: date_):
        return queryset.filter_for_registration_date(value)
