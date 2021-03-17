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


class ObjectRecordQuerySet(models.QuerySet):
    def filter_for_date(self, date):
        """
        Return records as seen on `date` from a formal historical perspective.

        The records that have their `start_at` date and `end_at` date between 
        the given `date`. If there is no `end_at` date, it means the record is
        still actual.
        
        If there are multiple records returned, the last added record (ie. with 
        the highest `index`) is the most actual record from a formal historical
        perspective.
        """
        return (
            self.filter(start_at__lte=date)
            .filter(models.Q(end_at__gte=date) | models.Q(end_at__isnull=True))
            .order_by("-index")
        )

    def filter_for_registration_date(self, date):
        """
        Return records as seen on `date` and later, from a material historical 
        perspective.

        Typically, the first record in the result set represents the record as 
        it is most actual from a material historical perspective.
        """
        return self.filter(registration_at__lte=date).order_by(
            "-registration_at", "-index"
        )
