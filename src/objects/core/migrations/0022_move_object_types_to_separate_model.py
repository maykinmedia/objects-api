import structlog
from urllib.parse import urlsplit, urlunsplit

from django.db import migrations
from django.db.models.functions import Length

from vng_api_common.utils import get_uuid_from_path

logger = structlog.stdlib.get_logger(__name__)


def get_service(model, url: str):
    "copy-pasted from zgw_consumers.Service method since it can't be used in migrations"
    split_url = urlsplit(url)
    scheme_and_domain = urlunsplit(split_url[:2] + ("", "", ""))

    candidates = (
        model.objects.filter(api_root__startswith=scheme_and_domain)
        .annotate(api_root_length=Length("api_root"))
        .order_by("-api_root_length")
    )

    # select the one matching
    for candidate in candidates.iterator():
        if url.startswith(candidate.api_root):
            return candidate

    return None


def move_objecttypes_to_model(apps, _):
    ObjectType = apps.get_model("core", "ObjectType")
    Object = apps.get_model("core", "Object")
    Service = apps.get_model("zgw_consumers", "Service")

    for object in Object.objects.all():
        service = get_service(Service, object.object_type)
        if not service:
            logger.warning(
                "missing_service_for_objecttype",
                object=object,
                object_type=object.object_type,
            )
            continue
        try:
            uuid = get_uuid_from_path(object.object_type)
        except ValueError:
            logger.warning(
                "invalid_objecttype",
                object=object,
                object_type=object.object_type,
            )
            continue

        object_type, created = ObjectType.objects.get_or_create(
            service=service, uuid=uuid
        )
        object.object_type_fk = object_type
        object.save()


def move_objecttypes_from_model(apps, _):
    Object = apps.get_model("core", "Object")

    for object in Object.objects.all():
        object.object_type = object.object_type_fk.url
        object.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_auto_20201222_1745"),
        ("zgw_consumers", "0011_remove_service_extra"),
    ]

    operations = [
        migrations.RunPython(move_objecttypes_to_model, move_objecttypes_from_model),
    ]
