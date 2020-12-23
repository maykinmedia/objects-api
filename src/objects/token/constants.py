from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class PermissionModes(DjangoChoices):
    read_only = ChoiceItem("read_only", _("Read-only"))
    read_and_write = ChoiceItem("read_and_write", _("Read and write"))
