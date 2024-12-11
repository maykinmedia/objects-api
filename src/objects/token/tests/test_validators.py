from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from objects.token.validators import validate_whitespace


class WhiteSpaceValidatorTestCase(SimpleTestCase):
    def test_characters_only(self):
        self.assertIsNone(validate_whitespace("test123"))

    def test_trailing_whitespace(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("test123  ")

    def test_leading_whitespace(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("  test123")

    def test_whitespace_in_between(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("test  123")

    def test_whitespace_only(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("  ")

    def test_trailing_tab_character(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("test123\t")

    def test_leading_tab_character(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("\ttest123")

    def test_tab_character_in_between(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("test\t123")

    def test_tab_characters_only(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("\t\t")

    def test_blank_value(self):
        with self.assertRaises(ValidationError):
            validate_whitespace("")
