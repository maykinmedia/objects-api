import datetime
import uuid

from django.contrib.gis.db.models import GeometryField
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from requests.exceptions import ConnectionError
from zds_client.client import ClientError
from zgw_consumers.models import Service

from .query import ObjectQuerySet, ObjectTypeQuerySet
from .utils import check_objecttype


class ObjectType(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name="object_types"
    )
    uuid = models.UUIDField(
        help_text=_("Unique identifier (UUID4) of the OBJECTTYPE in Objecttypes API")
    )
    _name = models.CharField(
        max_length=100,
        help_text=_("Cached name of the objecttype retrieved from the Objecttype API"),
    )

    objects = ObjectTypeQuerySet.as_manager()

    class Meta:
        unique_together = ("service", "uuid")

    def __str__(self):
        return f"{self.service.label}: {self._name}"

    @property
    def url(self):
        # zds_client.get_operation_url() can be used here but it increases HTTP overhead
        return f"{self.service.api_root}objecttypes/{self.uuid}"

    def clean(self):
        client = self.service.build_client()
        try:
            object_type_data = client.retrieve("objecttype", url=self.url)
        except (ClientError, ConnectionError, ValueError) as exc:
            raise ValidationError(f"Objecttype can't be requested: {exc}")

        if not self._name:
            self._name = object_type_data["name"]


class Object(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text="Unique identifier (UUID4)"
    )
    object_type = models.ForeignKey(
        ObjectType,
        on_delete=models.PROTECT,
    )

    objects = ObjectQuerySet.as_manager()

    def get_actual_record(self, date):
        """
        The record as seen on `date` from a formal historical perspective.

        The record that has its `start_at` date and `end_at` date between the
        given `date`. If there is no `end_at` date, it means the record is
        still actual. If there are multiple actual records, the last added
        record is the final actual record.
        """
        return (
            self.records.filter(start_at__lte=date)
            .filter(models.Q(end_at__gte=date) | models.Q(end_at__isnull=True))
            .order_by("-index")
            .first()
        )

    def get_registration_record(self, date):
        """
        The record as seen on `date` from a material historical perspective.

        The first (in time) record that has its `registration_at` on or before
        the given `date`.
        """
        return (
            self.records.filter(registration_at__lte=date)
            .order_by("-registration_at")
            .first()
        )

    @property
    def current_record(self):
        """
        The record as seen today from a formal historical perspective.

        The record that is "actual" today and (in case there are multiple
        "actual" records) with the highest index.
        """
        return self.get_actual_record(datetime.date.today())

    @property
    def last_record(self):
        """
        The latest record saved in the database, indicated by the highest
        index.
        """
        return self.records.order_by("-index").first()


class ObjectRecord(models.Model):
    index = models.PositiveIntegerField(
        default=1,
        help_text=_("Incremental index number of the object record."),
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

    class Meta:
        unique_together = ("object", "index")

    def __str__(self):
        return f"{self.version} ({self.start_at})"

    def clean(self):
        super().clean()

        check_objecttype(self.object.object_type, self.version, self.data)

    def save(self, *args, **kwargs):
        if not self.id and self.object.last_record:
            self.index = self.object.last_record.index + 1

            #  add end_at to previous record
            previous_record = self.object.last_record
            previous_record.end_at = self.start_at
            previous_record.save()

        super().save(*args, **kwargs)
