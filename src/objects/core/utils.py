from django.conf import settings
from django.core.exceptions import ValidationError

import jsonschema
import requests
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for

from objects.core import models
from objects.utils.cache import cache
from objects.utils.client import get_objecttypes_client


def check_objecttype_cached(
    object_type: "models.ObjectType", version: int, data: dict
) -> None:
    @cache(
        f"objecttypen-{object_type.uuid}:versions-{version}",
        timeout=settings.OBJECTTYPE_VERSION_CACHE_TIMEOUT,
    )
    def get_objecttype_version_response():
        with get_objecttypes_client(object_type.service) as client:
            try:
                return client.get_objecttype_version(object_type.uuid, version)
            except (requests.RequestException, requests.JSONDecodeError):
                raise ValidationError(
                    "Object type version can not be retrieved.",
                    code="invalid",
                )

    try:
        version_data = get_objecttype_version_response()
        jsonschema.validate(data, version_data["jsonSchema"])
    except KeyError:
        raise ValidationError(
            f"{object_type.versions_url} does not appear to be a valid objecttype.",
            code="invalid_key",
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ValidationError(exc.args[0], code="invalid_jsonschema")


def can_connect_to_objecttypes() -> bool:
    """
    check that all services of objecttypes are available
    """
    from zgw_consumers.models import Service

    for service in Service.objects.filter(object_types__isnull=False).distinct():
        with get_objecttypes_client(service) as client:
            if not client.can_connect:
                return False
    return True


def check_json_schema(json_schema: dict):
    schema_validator = validator_for(json_schema)
    try:
        schema_validator.check_schema(json_schema)
    except SchemaError as exc:
        raise ValidationError(exc.args[0]) from exc
