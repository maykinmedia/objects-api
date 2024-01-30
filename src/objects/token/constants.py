from django.db import models
from django.utils.translation import gettext_lazy as _


class PermissionModes(models.TextChoices):
    read_only = "read_only", _("Read-only")
    read_and_write = "read_and_write", _("Read and write")
