from django.utils.translation import ugettext_lazy as _

from djchoices import ChoiceItem, DjangoChoices


class Operators(DjangoChoices):
    exact = ChoiceItem("exact", _("equal to"))
    gt = ChoiceItem("gt", _("greater than"))
    gte = ChoiceItem("gte", _("greater than or equal to"))
    lt = ChoiceItem("lt", _("lower than"))
    lte = ChoiceItem("lte", _("lower than or equal to"))
    icontains = ChoiceItem(
        "icontains", _("case-insensitive partial matches on string values.")
    )
