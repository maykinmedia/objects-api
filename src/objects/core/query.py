import datetime

from django.db import models


class ObjectQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_anonymous:
            return self.none()
        allowed_object_types = user.object_permissions.values("object_type")
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
