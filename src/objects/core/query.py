from django.db import models

from vng_api_common.utils import get_uuid_from_path
from zgw_consumers.models import Service


class ObjectTypeQuerySet(models.QuerySet):
    def get_by_url(self, url):
        service = Service.get_service(url)
        uuid = get_uuid_from_path(url)
        return self.get(service=service, uuid=uuid)


class ObjectQuerySet(models.QuerySet):
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


class ObjectRecordQuerySet(models.QuerySet):
    def filter_for_token(self, token):
        if not token:
            return self.none()
        allowed_object_types = token.permissions.values("object_type")
        return self.filter(
            object__object_type__in=models.Subquery(allowed_object_types)
        )

    def keep_max_record_per_object(self):
        """
        Return records with the largest index for the object
        """
        filtered_records = self.order_by()
        grouped_records = (
            filtered_records.filter(object=models.OuterRef("object"))
            .values("object")
            .annotate(max_index=models.Max("index"))
            .values("max_index")
        )
        return self.filter(index=models.Subquery(grouped_records))

    def filter_for_date(self, date):
        """
        Return records as seen on `date` from a material historical perspective.

        The records that have their `start_at` date and `end_at` date between
        the given `date`. If there is no `end_at` date, it means the record is
        still actual.


        """
        return self.filter(start_at__lte=date).filter(
            models.Q(end_at__gte=date) | models.Q(end_at__isnull=True)
        )

    def filter_for_registration_date(self, date):
        """
        Return records as seen on `date` and later, from a formal historical
        perspective.
        """
        return self.filter(registration_at__lte=date)
