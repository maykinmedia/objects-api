from django.urls import reverse as _reverse
from django.utils.functional import lazy

VERSION = "v1"


def reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None):
    """always return api endpoints with predefined version"""
    viewname = f"{VERSION}:{viewname}"
    return _reverse(viewname, urlconf, args, kwargs, current_app)


reverse_lazy = lazy(reverse, str)
