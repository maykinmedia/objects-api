import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# includes tabs, carriage returns, newlines, form-feeds and vertical whitespace characters
WHITESPACE_PATTERN = re.compile(r".*\s.*")


def validate_whitespace(value: str) -> None:
    if not value:
        raise ValidationError(code="invalid", message=_("Blank values are not allowed"))

    if WHITESPACE_PATTERN.match(value):
        raise ValidationError(
            code="all-whitespace",
            message=_("Tokens cannot contain whitespace-like characters"),
        )
