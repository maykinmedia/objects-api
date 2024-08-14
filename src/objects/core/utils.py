from django.core.exceptions import ValidationError

import jsonschema
import requests
from zgw_consumers.client import build_client


def check_objecttype(object_type, version, data):
    client = build_client(object_type.service)
    objecttype_version_url = f"{object_type.url}/versions/{version}"

    try:
        response = client.get(objecttype_version_url)
    except requests.RequestException as exc:
        msg = f"Object type version can not be retrieved: {exc.args[0]}"
        raise ValidationError(msg)

    try:
        response_data = response.json()
    except requests.JSONDecodeError:
        raise ValidationError("Object type doesn't have retrievable data")

    try:
        schema = response_data.get("jsonSchema")
    except KeyError:
        msg = f"{objecttype_version_url} does not appear to be a valid objecttype."
        raise ValidationError(msg)

    # TODO: Set warning header if objecttype is not published.

    try:
        jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError as exc:
        raise ValidationError(exc.args[0]) from exc


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
