from django.db import models
from django.utils.translation import gettext_lazy as _


class Operators(models.TextChoices):
    exact = "exact", _("equal to")
    gt = "gt", _("greater than")
    gte = "gte", _("greater than or equal to")
    lt = "lt", _("lower than")
    lte = "lte", _("lower than or equal to")
    icontains = "icontains", _("case-insensitive partial match")
