import uuid
from datetime import date

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .constants import RecordType


class Object(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text="Unique identifier (UUID4)"
    )
    object_type = models.URLField(
        _("object type"), help_text=_("Url reference to OBJECTTYPE in Objecttypes API")
    )
    version = models.PositiveSmallIntegerField(
        _("version"), help_text=_("Version of the OBJECTTYPE")
    )

    @property
    def record_material(self, material_date=None):
        material_date = material_date or date.today()
        return (
            self.records.filter(material_date__lte=material_date)
            .order_by("-material_date", "-id")
            .first()
        )

    @property
    def record_registration(self, registration_date=None):
        registration_date = registration_date or date.today()
        return (
            self.records.filter(registration_date__lte=registration_date)
            .order_by("-registration_date", "-id")
            .first()
        )

    @property
    def status(self):
        return self.record_material.record_type


class ObjectRecord(models.Model):
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name="records")
    data = JSONField(
        _("data"), help_text=_("Object data, based on OBJECTTYPE"), default=dict
    )
    record_type = models.CharField(
        _("record type"),
        max_length=50,
        choices=RecordType.choices,
        default=RecordType.created,
    )
    material_date = models.DateField(_("material date"))
    registration_date = models.DateField(_("registration date"), default=date.today)
