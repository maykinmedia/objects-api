import binascii
import os

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
        help_text=_("Organizations which has an access to the API"),
    )
    last_modified = models.DateTimeField(
        _("last modified"),
        auto_now=True,
        help_text=_("Last date when the token was modified"),
    )
    created = models.DateTimeField(
        _("created"), auto_now_add=True, help_text=_("Date when the token was created")
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

    class Meta:
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
