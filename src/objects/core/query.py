import datetime

from django.db import models


class ObjectQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        if user.is_anonymous:
            return self.none()
        allowed_object_types = user.object_permissions.values("object_type")
        return self.filter(object_type__in=models.Subquery(allowed_object_types))

    def filter_for_date(self, date=None):
        actual_date = date or datetime.date.today()
        return (
            self.filter(records__start_date__lte=actual_date)
            .filter(
                models.Q(records__end_date__gte=actual_date)
                | models.Q(records__end_date__isnull=True)
            )
            .distinct()
        )
