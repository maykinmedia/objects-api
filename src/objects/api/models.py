import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField


class Object(models.Model):
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, help_text="Unique identifier (UUID4)"
    )
    object_type = models.URLField(
        _("object type"), help_text=_("Url reference to OBJECTTYPE in Objecttypes API")
    )
    version = models.SmallIntegerField(
        _("version"), help_text=_("Version of the OBJECTTYPE")
    )
    data = JSONField(_("data"), help_text=_("Object data, based on OBJECTTYPE"), default={})
