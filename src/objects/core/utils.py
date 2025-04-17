from django.conf import settings
from django.core.exceptions import ValidationError

import jsonschema
import requests
from zgw_consumers.client import build_client

from objects.utils.cache import cache


def check_objecttype(object_type, version, data):
    @cache(
        f"objecttypen-{object_type.uuid}:versions-{version}",
        timeout=settings.OBJECTTYPE_VERSION_CACHE_TIMEOUT,
    )
    def get_objecttype_version_response():
        client = build_client(object_type.service)
        try:
            return client.get(f"{object_type.versions_url}/{version}")
        except requests.RequestException:
            raise ValidationError(
                {"type": "Object type version can not be retrieved."},
                code="invalid",
            )

    response = get_objecttype_version_response()

    try:
        response_data = response.json()
        schema = response_data["jsonSchema"]
        jsonschema.validate(data, schema)
    except requests.JSONDecodeError:
        raise ValidationError(
            {"type": "Object type doesn't have retrievable data."},
            code="invalid_json",
        )
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

    objecttypes_services = Service.objects.filter(object_types__isnull=False).distinct()
    for service in objecttypes_services:
        client = build_client(service)

        try:
            client.get("objecttypes")
        except requests.RequestException:
            return False

    return True
