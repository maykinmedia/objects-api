import datetime
import uuid

from django.contrib.gis.db.models import GeometryField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

import requests
from requests.exceptions import ConnectionError
from zgw_consumers.client import build_client
from zgw_consumers.models import Service

from .query import ObjectQuerySet, ObjectRecordQuerySet, ObjectTypeQuerySet
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
        client = build_client(self.service)
        try:
            response = client.get(url=self.url)
        except (requests.RequestException, ConnectionError, ValueError) as exc:
            raise ValidationError(f"Objecttype can't be requested: {exc}")

        try:
            object_type_data = response.json()
        except requests.exceptions.JSONDecodeError:
            ValidationError(f"Object type version didn't have any data")

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

    @property
    def current_record(self):
        return self.records.filter_for_date(datetime.date.today()).first()

    @property
    def last_record(self):
        return self.records.order_by("-index").first()

    @property
    def record(self):
        # `actual_records` attribute is set in ObjectViewSet.get_queryset
        if getattr(self, "actual_records", None):
            return self.actual_records[0]

        # for create and update
        return self.current_record


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
    data = models.JSONField(
        _("data"),
        help_text=_("Object data, based on OBJECTTYPE"),
        default=dict,
        encoder=DjangoJSONEncoder,
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
            "Point, linestring or polygon object which represents the coordinates of the "
            "object. Geometry can be added only if the related OBJECTTYPE allows this "
            "(`OBJECTTYPE.allowGeometry = true` or `OBJECTTYPE.allowGeometry` doesn't "
            "exist)"
        ),
    )

    objects = ObjectRecordQuerySet.as_manager()

    class Meta:
        unique_together = ("object", "index")

    def __str__(self):
        return f"{self.version} ({self.start_at})"

    def clean(self):
        super().clean()

        if hasattr(self.object, "object_type") and self.version and self.data:
            check_objecttype(self.object.object_type, self.version, self.data)

    def save(self, *args, **kwargs):
        if not self.id and self.object.last_record:
            self.index = self.object.last_record.index + 1

            #  add end_at to previous record
            previous_record = self.object.last_record
            previous_record.end_at = self.start_at
            previous_record.save()

        super().save(*args, **kwargs)
