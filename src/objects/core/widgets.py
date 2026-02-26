import json

from jsonsuit.widgets import JSONSuit as _JSONSuit


class JSONSuit(_JSONSuit):
    initial = dict()

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        try:
            json.loads(value)
        except ValueError:
            # The supplied value is not valid JSON, use the original value as
            # a fallback
            value = json.dumps(self.initial)
        return super().render(name, value, attrs)
