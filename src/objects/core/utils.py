from django.core.exceptions import ValidationError

import jsonschema
from zds_client.client import ClientError


def check_objecttype(object_type, version, data):
    if not data:
        return

    client = object_type.service.build_client()
    objecttype_version_url = f"{object_type.url}/versions/{version}"

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
