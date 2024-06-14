from django.core.exceptions import ValidationError

import jsonschema
from requests.exceptions import RequestException
from zds_client.client import ClientError


def check_objecttype(object_type, version, data):
    client = object_type.service.build_client()
    objecttype_version_url = f"{object_type.url}/versions/{version}"

    try:
        response = client.retrieve("objectversion", url=objecttype_version_url)
    except ClientError as exc:
        msg = f"Object type version can not be retrieved: {exc.args[0]}"
        raise ValidationError(msg)

    try:
        schema = response["jsonSchema"]
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
        client = service.build_client()

        try:
            client.request("objecttypes", "objecttype_list")
        except (ClientError, RequestException):
            return False

    return True
