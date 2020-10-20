from django.utils.translation import ugettext_lazy as _

from django_filters import filters
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_help_text

from objects.core.models import Object

from .constants import Operators
from .utils import display_choice_values_for_help_text, is_number
from .validators import validate_data_attrs


class ObjectFilterSet(FilterSet):
    type = filters.CharFilter(
        field_name="object_type", help_text=get_help_text("core.Object", "object_type")
    )
    data_attrs = filters.CharFilter(
        method="filter_data_attrs",
        validators=[validate_data_attrs],
        help_text=_(
            """Only include objects that have attributes with certain values.
Data filtering expressions are comma-separated and are structured as follows:
A valid parameter value has the form `key__operator__value`.
`key` is the attribute name, `operator` is the comparison operator to be used and `value` is the attribute value.
Note: Values can be string or numeric. Dates are not supported.

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
        fields = ("type", "data_attrs")

    def filter_data_attrs(self, queryset, name, value):
        variable, operator, val = value.rsplit("__", 2)
        val_numeric = float(val) if is_number(val) else None

        if operator != "exact":
            # only numeric
            return queryset.filter(
                **{f"records__data__{variable}__{operator}": val_numeric}
            ).distinct()

        #  for exact operator try to filter on string value first
        result = queryset.filter(**{f"records__data__{variable}": val}).distinct()
        if result.count() == 0 and is_number(val):
            result = queryset.filter(
                **{f"records__data__{variable}": val_numeric}
            ).distinct()
        return result
