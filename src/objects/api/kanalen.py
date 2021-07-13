from django.conf import settings

from vng_api_common.notifications.kanalen import Kanaal

from objects.core.models import Object

KANAAL_OBJECTEN = Kanaal(
    settings.NOTIFICATIONS_KANAAL,
    main_resource=Object,
    kenmerken=("object_type",),
)
