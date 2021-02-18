import datetime

from django.db import models

from vng_api_common.utils import get_uuid_from_path
from zgw_consumers.models import Service


class ObjectTypeQuerySet(models.QuerySet):
    def get_by_url(self, url):
        service = Service.get_service(url)
        uuid = get_uuid_from_path(url)
        return self.get(service=service, uuid=uuid)


class ObjectQuerySet(models.QuerySet):
    def filter_for_token(self, token):
        if not token:
            return self.none()
        allowed_object_types = token.permissions.values("object_type")
        return self.filter(object_type__in=models.Subquery(allowed_object_types))

    def filter_for_date(self, date):
        return (
            self.filter(records__start_at__lte=date)
            .filter(
                models.Q(records__end_at__gte=date)
                | models.Q(records__end_at__isnull=True)
            )
            .distinct()
        )

    def filter_for_registration_date(self, date):
        return self.filter(records__registration_at__lte=date).distinct()
