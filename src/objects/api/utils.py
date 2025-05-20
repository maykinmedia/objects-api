from datetime import date

from django.db import models

from objects.typing import JSONValue


def string_to_value(value: str) -> str | float | date:
    if is_number(value):
        return float(value)
    elif is_date(value):
        return date.fromisoformat(value)

    return value


def is_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False

    return True


def is_number(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False

    return True


def display_choice_values_for_help_text(choices: type[models.TextChoices]) -> str:
    items = []

    for key, value in choices.choices:
        item = f"* `{key}` - {value}"
        items.append(item)

    return "\n".join(items)


def merge_patch(target: JSONValue, patch: JSONValue) -> dict[str, JSONValue]:
    """Merge two objects together recursively.

    This is inspired by https://datatracker.ietf.org/doc/html/rfc7396 - JSON Merge Patch,
    but deviating in some cases to suit our needs.
    """

    if not isinstance(patch, dict):
        return patch

    if not isinstance(target, dict):
        # Ignore the contents and set it to an empty dict
        target = {}
    for k, v in patch.items():
        # According to RFC, we should remove k from target
        # if v is None. This is where we deviate.
        target[k] = merge_patch(target.get(k), v)

    return target
