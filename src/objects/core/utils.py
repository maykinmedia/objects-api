from django.conf import settings
from django.core.exceptions import ValidationError

import jsonschema
import requests

from objects.utils.cache import cache
from objects.utils.client import get_objecttypes_client


def check_objecttype(object_type, version, data):
    @cache(
        f"objecttypen-{object_type.uuid}:versions-{version}",
        timeout=settings.OBJECTTYPE_VERSION_CACHE_TIMEOUT,
    )
    def get_objecttype_version_response():
        client = get_objecttypes_client(object_type.service)
        try:
            return client.get_objecttype_version(object_type.uuid, version)
        except (requests.RequestException, requests.JSONDecodeError):
            raise ValidationError(
                {"type": "Object type version can not be retrieved."},
                code="invalid",
            )

    try:
        vesion_data = get_objecttype_version_response()

        jsonschema.validate(data, vesion_data["jsonSchema"])
    except KeyError:
        raise ValidationError(
            {
                "type": f"{object_type.versions_url} does not appear to be a valid objecttype."
            },
            code="invalid_key",
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ValidationError({"data": exc.args[0]}, code="invalid_jsonschema")


def can_connect_to_objecttypes() -> bool:
    """
    check that all services of objecttypes are available
    """
    from zgw_consumers.models import Service

    for service in Service.objects.filter(object_types__isnull=False).distinct():
        client = get_objecttypes_client(service)
        if not client.can_connect:
            return False
    return True
