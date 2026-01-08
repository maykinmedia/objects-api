from django.db import models
from django.utils.translation import gettext_lazy as _


class ObjectVersionStatus(models.TextChoices):
    published = "published", _("Published")
    draft = "draft", _("Draft")
    deprecated = "deprecated", _("Deprecated")


class DataClassificationChoices(models.TextChoices):
    open = "open", _("Open")
    intern = "intern", _("Intern")
    confidential = "confidential", _("Confidential")
    strictly_confidential = "strictly_confidential", _("Strictly confidential")


class UpdateFrequencyChoices(models.TextChoices):
    real_time = "real_time", _("Real-time")
    hourly = "hourly", _("Hourly")
    daily = "daily", _("Daily")
    weekly = "weekly", _("Weekly")
    monthly = "monthly", _("Monthly")
    yearly = "yearly", _("Yearly")
    unknown = "unknown", _("Unknown")


class ReferenceType(models.TextChoices):
    zaak = "zaak", _("Zaak")
