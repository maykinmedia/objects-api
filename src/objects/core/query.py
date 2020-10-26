from django.db import models


class ObjectQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        allowed_object_types = user.object_permissions.values("object_type")
        return self.filter(object_type__in=models.Subquery(allowed_object_types))
