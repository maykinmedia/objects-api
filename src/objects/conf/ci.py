"""
Continuous integration settings module.
"""

import os

from open_api_framework.conf.utils import mute_logging

os.environ.setdefault("SECRET_KEY", "dummy")
os.environ.setdefault("IS_HTTPS", "no")
os.environ.setdefault("ENVIRONMENT", "ci")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
os.environ.setdefault("OTEL_SERVICE_NAME", "objects-ci")

os.environ.setdefault("DB_USER", "postgres")
os.environ.setdefault("DB_PASSWORD", "postgres")

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

CELERY_BROKER_TRANSPORT_OPTIONS = {
    # when running in CI with a deliberately broken broker URL, tests should fail/error
    # instead of retrying forever if the broker isn't available (which it won't be).
    "max_retries": 0,
}
