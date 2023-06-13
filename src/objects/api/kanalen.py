from collections import defaultdict
from typing import Dict

from django.conf import settings
from django.db import models

from notifications_api_common.kanalen import Kanaal

from objects.core.models import Object, ObjectRecord


class ObjectKanaal(Kanaal):
    def __init__(
        self, label: str, main_resource: models.base.ModelBase, kenmerken: tuple = None
    ):
        self.label = label
        self.main_resource = main_resource

        self.usage = defaultdict(list)  # filled in by metaclass of notifications

        # check that we're refering to existing fields
        self.kenmerken = kenmerken or ()

    def get_kenmerken(self, obj: models.Model, data: Dict = None) -> Dict:
        data = data or {}
        return {
            kenmerk: data.get("type") or obj.object.object_type.url
            if kenmerk == "object_type"
            else data.get(kenmerk, getattr(obj, kenmerk))
            for kenmerk in self.kenmerken
        }


KANAAL_OBJECTEN = ObjectKanaal(
    settings.NOTIFICATIONS_KANAAL,
    main_resource=ObjectRecord,
    kenmerken=("object_type",),
)
