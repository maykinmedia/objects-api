from django.test import TestCase

from bs4 import BeautifulSoup

from objects.core.widgets import JSONSuit


class JSONSuitTestCase(TestCase):
    def test_render_valid_json_schema(self):
        widget = JSONSuit()

        widget.initial = {"foo": "bar"}

        rendered = widget.render("field_name", '{"bar": "foo"}')
        soup = BeautifulSoup(rendered, "html.parser")

        textarea = soup.find("textarea")
        self.assertEqual(
            textarea.text.strip(), soup.find("code").attrs["data-raw"], '{"bar": "foo"}'
        )

    def test_render_invalid_json_schema_fallback(self):
        widget = JSONSuit()

        rendered = widget.render("field_name", "{}{")
        soup = BeautifulSoup(rendered, "html.parser")

        textarea = soup.find("textarea")
        self.assertEqual(
            textarea.text.strip(), soup.find("code").attrs["data-raw"], "{}"
        )

    def test_render_invalid_json_schema_initial(self):
        widget = JSONSuit()

        widget.initial = {"foo": "bar"}

        rendered = widget.render("field_name", "{}{")
        soup = BeautifulSoup(rendered, "html.parser")

        textarea = soup.find("textarea")
        self.assertEqual(
            textarea.text.strip(), soup.find("code").attrs["data-raw"], '{"foo": "bar"}'
        )
