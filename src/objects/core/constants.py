from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class RecordType(DjangoChoices):
    created = ChoiceItem("created", _("Created"))
    changed = ChoiceItem("changed", _("Changed"))
    destroyed = ChoiceItem("destroyed", _("Destroyed"))
