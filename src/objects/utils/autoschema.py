from django.utils.translation import ugettext_lazy as _

from drf_yasg import openapi
from vng_api_common.inspectors.view import AutoSchema as _AutoSchema

from .serializers import DynamicFieldsMixin


class AutoSchema(_AutoSchema):
    def has_dynamic_fields(self):
        if self.method != "GET":
            return False

        serializer = self.get_request_serializer() or self.get_view_serializer()
        if not serializer:
            return False

        return isinstance(serializer, DynamicFieldsMixin)

    def add_manual_parameters(self, parameters):
        base = super().add_manual_parameters(parameters)

        if self.has_dynamic_fields():
            base += [
                openapi.Parameter(
                    name="fields",
                    type=openapi.TYPE_STRING,
                    in_=openapi.IN_QUERY,
                    required=False,
                    description=_(
                        "Comma-separated fields, which should be displayed in the response. "
                        "For example: 'url, uuid, record__geometry'. Attributes inside `record.data` "
                        "field are not supported for this parameter. "
                    ),
                )
            ]

        return base
