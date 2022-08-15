from datetime import date
from typing import Union

from djchoices import DjangoChoices


def string_to_value(value: str) -> Union[str, float, date]:
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


def display_choice_values_for_help_text(choices: DjangoChoices) -> str:
    items = []

    for key, value in choices.choices:
        description = getattr(choices.get_choice(key), "description", None)
        if description:
            item = f"* `{key}` - ({value}) {description}"
        else:
            item = f"* `{key}` - {value}"
        items.append(item)

    return "\n".join(items)
