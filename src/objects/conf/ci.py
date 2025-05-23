"""
Continuous integration settings module.
"""

import os

from open_api_framework.conf.utils import mute_logging

os.environ.setdefault("SECRET_KEY", "dummy")
os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("ENVIRONMENT", "ci")

from .base import *  # noqa isort:skip

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    # https://github.com/jazzband/django-axes/blob/master/docs/configuration.rst#cache-problems
    "axes": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
    "oas": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "sessions": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "oidc": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

mute_logging(LOGGING)


#
# Django-axes
#
AXES_BEHIND_REVERSE_PROXY = False

NOTIFICATIONS_DISABLED = True
