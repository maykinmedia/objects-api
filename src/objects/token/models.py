import binascii
import os

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from objects.core.models import ObjectType

from .constants import PermissionModes


class TokenAuth(models.Model):
    token = models.CharField(_("token"), max_length=40, primary_key=True)
    contact_person = models.CharField(
        _("contact person"),
        max_length=200,
        help_text=_("Name of the person in the organization who can access the API"),
    )
    email = models.EmailField(
        _("email"), help_text=_("Email of the person, who can access the API")
    )
    organization = models.CharField(
        _("organization"),
        max_length=200,
        blank=True,
        help_text=_("Organization which has access to the API"),
    )
    last_modified = models.DateTimeField(
        _("last modified"),
        auto_now=True,
        help_text=_("Last date when the token was modified"),
    )
    created = models.DateTimeField(
        _("created"), auto_now_add=True, help_text=_("Date when the token was created")
    )
    application = models.CharField(
        _("application"),
        max_length=200,
        blank=True,
        help_text=_("Application which has access to the API"),
    )
    administration = models.CharField(
        _("administration"),
        max_length=200,
        blank=True,
        help_text=_("Administration which has access to the API"),
    )

    object_types = models.ManyToManyField(
        "core.ObjectType",
        through="token.Permission",
        help_text=_("Object types which can be accessed"),
    )

    class Meta:
        verbose_name = _("token authorization")
        verbose_name_plural = _("token authorizations")

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    def generate_token(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def get_permission_for_object_type(self, object_type: ObjectType):
        if not self.permissions.filter(object_type=object_type).exists():
            return None
        return self.permissions.get(object_type=object_type)


class Permission(models.Model):
    token_auth = models.ForeignKey(
        "token.TokenAuth", on_delete=models.CASCADE, related_name="permissions"
    )
    object_type = models.ForeignKey(
        "core.ObjectType", on_delete=models.CASCADE, related_name="permissions"
    )
    mode = models.CharField(
        _("mode"),
        max_length=20,
        choices=PermissionModes.choices,
        help_text=_("Permission mode"),
    )
    use_fields = models.BooleanField(
        _("use fields"), default=False, help_text=_("Use field-based authorization")
    )
    # todo validate use_fields can't be true with empty fields
    fields = ArrayField(
        models.CharField(_("field"), max_length=30),
        blank=True,
        default=list,
        help_text=_(
            "Fields allowed for this token. Supports only first level of the `record.data` properties"
        ),
    )

    class Meta:
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
        unique_together = ("token_auth", "object_type")
