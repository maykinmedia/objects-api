from django.urls import reverse as _reverse
from django.utils.functional import lazy

VERSION = 1


def reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None):
    """always return api endpoints with predefined version"""
    if args:
        args.insert(0, VERSION)

    else:
        kwargs = kwargs or {}
        kwargs["version"] = VERSION
    return _reverse(viewname, urlconf, args, kwargs, current_app)


reverse_lazy = lazy(reverse, str)
