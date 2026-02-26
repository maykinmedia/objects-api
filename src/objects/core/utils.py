from django.core.exceptions import ValidationError

import jsonschema
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for

from objects.core import models


def check_objecttype(
    object_type: "models.ObjectType", version: int, data: dict
) -> None:
    try:
        version_data = object_type.versions.get(version=version)
        jsonschema.validate(data, version_data.json_schema)
    except models.ObjectTypeVersion.DoesNotExist:
        raise ValidationError(
            f"Object type {object_type} version: {version} does not appear to exist.",
            code="invalid_key",
        )
    except jsonschema.exceptions.ValidationError as exc:
        raise ValidationError(exc.args[0], code="invalid_jsonschema")


def check_json_schema(json_schema: dict):
    schema_validator = validator_for(json_schema)
    try:
        schema_validator.check_schema(json_schema)
    except SchemaError as exc:
        raise ValidationError(exc.args[0]) from exc
