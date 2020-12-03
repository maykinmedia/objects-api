import json

from django.core.exceptions import ValidationError

import jsonschema
import requests
from zgw_consumers.models import Service


def check_objecttype(object_type, version, data):
    if not data:
        return

    objecttype_version_url = f"{object_type}/versions/{version}"

    auth = Service.get_auth_header(object_type)
    response = requests.get(objecttype_version_url, headers=auth)

    if response.status_code == 404:
        msg = f"{object_type} or version {version} doesn't exist."
        raise ValidationError(msg)

    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ValidationError(exc.args[0]) from exc

    try:
        json_data = response.json()
        schema = json_data["jsonSchema"]
    except json.decoder.JSONDecodeError:
        msg = f"{objecttype_version_url} returned invalid JSON."
        raise ValidationError(msg)
    except KeyError:
        msg = f"{objecttype_version_url} does not appear to be a valid objecttype."
        raise ValidationError(msg)

    # TODO: Set warning header if objecttype is not published.

    try:
        jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError as exc:
        raise ValidationError(exc.args[0]) from exc
