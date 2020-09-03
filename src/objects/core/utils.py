from django.core.exceptions import ValidationError

import jsonschema
import requests


def check_objecttype(object_type, version, data):
    if not data:
        return

    response = requests.get(object_type)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ValidationError(exc.args[0]) from exc

    type_data = response.json()
    versions = list(
        filter(lambda x: x.get("version") == version, type_data.get("versions", []))
    )
    try:
        version_data = versions[0]
    except IndexError:
        msg = f"{object_type} doesn't include JSON schema for version {version}"
        raise ValidationError(msg)

    schema = version_data["jsonSchema"]
    try:
        jsonschema.validate(data, schema)
    except jsonschema.exceptions.ValidationError as exc:
        raise ValidationError(exc.args[0]) from exc
