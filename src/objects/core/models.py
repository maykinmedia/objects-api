import uuid
from datetime import date

from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import check_objecttype


class Object(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text="Unique identifier (UUID4)"
    )
    object_type = models.URLField(
        _("object type"), help_text=_("Url reference to OBJECTTYPE in Objecttypes API")
    )

    @property
    def current_record(self):
        today = date.today()
        return (
            self.records.filter(start_date__lte=today)
            .filter(models.Q(end_date__gte=today) | models.Q(end_date__isnull=True))
            .first()
        )

    @property
    def last_record(self):
        return self.records.order_by("-start_date", "-id").first()


class ObjectRecord(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4, help_text="Unique identifier (UUID4)", unique=True
    )
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name="records")
    version = models.PositiveSmallIntegerField(
        _("version"),
        help_text=_("Version of the OBJECTTYPE for data in the object record"),
    )
    data = JSONField(
        _("data"), help_text=_("Object data, based on OBJECTTYPE"), default=dict
    )
    start_date = models.DateField(
        _("start date"), help_text=_("Legal start date of the object record")
    )
    end_date = models.DateField(
        _("end date"), null=True, help_text=_("Legal end date of the object record")
    )
    registration_date = models.DateField(
        _("registration date"),
        default=date.today,
        help_text=_("The date when the record was registered in the system"),
    )
    correct = models.OneToOneField(
        "core.ObjectRecord",
        on_delete=models.PROTECT,
        related_name="corrected",
        null=True,
        blank=True,
        help_text=_("Object record which corrects the current record"),
    )
    geometry = GeometryField(
        _("geometry"),
        blank=True,
        null=True,
        help_text=_(
            "Point, linestring or polygon object which represents the coordinates of the object"
        ),
    )

    def __str__(self):
        return f"{self.version} ({self.start_date})"

    def clean(self):
        super().clean()
        print(self.geometry)

        check_objecttype(self.object.object_type, self.version, self.data)

    def save(self, *args, **kwargs):
        if not self.id and self.object.last_record:
            #  add end_date to previous record
            previous_record = self.object.last_record
            previous_record.end_date = self.start_date
            previous_record.save()

        super().save(*args, **kwargs)
