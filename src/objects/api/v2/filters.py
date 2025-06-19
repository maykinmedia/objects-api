from datetime import date as date_

from django import forms
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from django_filters import filters
from rest_framework import serializers
from vng_api_common.filtersets import FilterSet

from objects.core.models import ObjectRecord, ObjectType
from objects.utils.filters import ManyCharFilter, ObjectTypeFilter

from ..constants import Operators
from ..utils import display_choice_values_for_help_text, string_to_value
from ..validators import validate_data_attr, validate_data_attrs

DATA_ATTR_VALUE_HELP_TEXT = f"""A valid parameter value has the form `key__operator__value`.
`key` is the attribute name, `operator` is the comparison operator to be used and `value` is the attribute value.
Note: Values can be string, numeric, or dates (ISO format; YYYY-MM-DD).

Valid operator values are:
{display_choice_values_for_help_text(Operators)}

`value` may not contain double underscore or comma characters.
`key` may not contain comma characters and includes double underscore only if it indicates nested attributes.

"""

DATA_ATTRS_HELP_TEXT = _(
    """**DEPRECATED: Use 'data_attr' instead**.
Only include objects that have attributes with certain values.
Data filtering expressions are comma-separated and are structured as follows:

%(value_part_help_text)s

Example: in order to display only objects with `height` equal to 100, query `data_attrs=height__exact__100`
should be used. If `height` is nested inside `dimensions` attribute, query should look like
`data_attrs=dimensions__height__exact__100`

`value` may not contain comma, since commas are used as separator between filtering expressions.
If you want to use commas in `value` you can use `data_attr` query parameter.
"""
) % {"value_part_help_text": DATA_ATTR_VALUE_HELP_TEXT}

DATA_ATTR_HELP_TEXT = _(
    """Only include objects that have attributes with certain values.

%(value_part_help_text)s

Example: in order to display only objects with `height` equal to 100, query `data_attr=height__exact__100`
should be used. If `height` is nested inside `dimensions` attribute, query should look like
`data_attr=dimensions__height__exact__100`

This filter is very similar to the old `data_attrs` filter, but it has two differences:

* `value` may contain commas
* only one filtering expression is allowed

If you want to use several filtering expressions, just use this `data_attr` several times in the query string.
Example: `data_attr=height__exact__100&data_attr=naam__icontains__boom`
"""
) % {"value_part_help_text": DATA_ATTR_VALUE_HELP_TEXT}


def filter_data_attr_value_part(value_part: str, queryset: QuerySet) -> QuerySet:
    """
    filter one value part for data_attr and data_attrs filters
    """
    variable, operator, str_value = value_part.rsplit("__", 2)
    real_value = string_to_value(str_value)

    if operator == "exact":
        #  for exact operator try to filter on string and numeric values
        in_vals = [str_value]
        if real_value != str_value:
            in_vals.append(real_value)
        queryset = queryset.filter(**{f"data__{variable}__in": in_vals})
    elif operator == "icontains":
        # icontains treats everything like strings
        queryset = queryset.filter(**{f"data__{variable}__icontains": str_value})
    elif operator == "in":
        # in must be a list
        values = str_value.split("|")
        queryset = queryset.filter(**{f"data__{variable}__in": values})

    else:
        # gt, gte, lt, lte operators
        queryset = queryset.filter(**{f"data__{variable}__{operator}": real_value})
    return queryset


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
        help_text=DATA_ATTRS_HELP_TEXT,
    )

    data_attr = ManyCharFilter(
        method="filter_data_attr",
        validators=[validate_data_attr],
        help_text=DATA_ATTR_HELP_TEXT,
    )

    data_icontains = filters.CharFilter(
        method="filter_data_icontains",
        help_text=_("Search in all `data` values of string properties."),
    )

    class Meta:
        model = ObjectRecord
        fields = ("type", "data_attrs", "data_attr", "date", "registrationDate")
        form = ObjectRecordFilterForm

    def filter_data_attrs(self, queryset, name, value: str):
        parts = value.split(",")

        for value_part in parts:
            queryset = filter_data_attr_value_part(value_part, queryset)

        return queryset

    def filter_data_attr(self, queryset, name, value: list):
        for value_part in value:
            queryset = filter_data_attr_value_part(value_part, queryset)

        return queryset

    def filter_data_icontains(self, queryset, name, value: str):
        # TODO consider using `data__icontains=value` here instead? This does mean regexes
        # are no longer supported, but it's a lot more efficient and the docs do not
        # clearly state that regexes were supported anyway. A different parameter could
        # be added to allow regex search

        # WHERE clause has jsonpath: where data @? '$.** ? (@ like_regex "$value" flag "i")'
        where_str = "core_objectrecord.data @? CONCAT('$.** ? (@ like_regex \"',%s::text,'\" flag \"i\")')::jsonpath"
        return queryset.extra(where=[where_str], params=[value])

    def filter_date(self, queryset, name, value: date_):
        """actual filtering is performed in the viewset"""
        return queryset

    def filter_registration_date(self, queryset, name, value: date_):
        """actual filtering is performed in the viewset"""
        return queryset
