import datetime
import uuid

from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .query import ObjectQuerySet
from .utils import check_objecttype


class Object(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text="Unique identifier (UUID4)"
    )
    object_type = models.URLField(
        _("object type"), help_text=_("Url reference to OBJECTTYPE in Objecttypes API")
    )

    objects = ObjectQuerySet.as_manager()

    def get_actual_record(self, date):
        return (
            self.records.filter(start_at__lte=date)
            .filter(models.Q(end_at__gte=date) | models.Q(end_at__isnull=True))
            .order_by("-pk")
            .first()
            # TODO: pk should prolly be index once added.
        )

    def get_registration_record(self, date):
        return (
            self.records.filter(registration_at__lte=date)
            .order_by("-registration_at")
            .first()
        )

    @property
    def current_record(self):
        return self.get_actual_record(datetime.date.today())

    @property
    def last_record(self):
        return self.records.order_by("-start_at", "-id").first()


class ObjectRecord(models.Model):
    # index = models.PositiveIntegerField(help_text="Incremental index number of the object record.", default=1)
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
    start_at = models.DateField(
        _("start at"), help_text=_("Legal start date of the object record")
    )
    end_at = models.DateField(
        _("end at"), null=True, help_text=_("Legal end date of the object record")
    )
    registration_at = models.DateField(
        _("registration at"),
        default=datetime.date.today,
        help_text=_("The date when the record was registered in the system"),
    )
    correct = models.OneToOneField(
        "core.ObjectRecord",
        verbose_name="correction for",
        on_delete=models.CASCADE,
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
        return f"{self.version} ({self.start_at})"

    def clean(self):
        super().clean()

        check_objecttype(self.object.object_type, self.version, self.data)

    def save(self, *args, **kwargs):
        if not self.id and self.object.last_record:
            # self.index = self.object.last_record.index + 1

            #  add end_at to previous record
            previous_record = self.object.last_record
            previous_record.end_at = self.start_at
            previous_record.save()

        super().save(*args, **kwargs)
