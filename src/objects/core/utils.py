from django.core.exceptions import ValidationError

import jsonschema
from zds_client.client import ClientError
from zgw_consumers.models import Service


def check_objecttype(object_type, version, data):
    if not data:
        return

    client = Service.get_client(object_type)
    objecttype_version_url = f"{object_type}/versions/{version}"

    try:
        response = client.retrieve("objectversion", url=objecttype_version_url)
    except ClientError as exc:
        raise ValidationError(exc.args[0]) from exc

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
