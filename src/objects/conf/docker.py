import os

os.environ.setdefault("DB_USER", os.getenv("DB_USER", "objects"))
os.environ.setdefault("DB_NAME", os.getenv("DB_NAME", "objects"))
os.environ.setdefault("DB_PASSWORD", os.getenv("DB_PASSWORD", "objects"))
os.environ.setdefault("DB_HOST", os.getenv("DB_HOST", "db"))

from .base import *  # noqa isort:skip
from .utils import config  # noqa isort:skip

#
# Standard Django settings.
#
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    # https://github.com/jazzband/django-axes/blob/master/docs/configuration.rst#cache-problems
    "axes_cache": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "oidc": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

# Deal with being hosted on a subpath
subpath = config("SUBPATH", None)
if subpath:
    if not subpath.startswith("/"):
        subpath = f"/{subpath}"

    FORCE_SCRIPT_NAME = subpath
    STATIC_URL = f"{FORCE_SCRIPT_NAME}{STATIC_URL}"
    MEDIA_URL = f"{FORCE_SCRIPT_NAME}{MEDIA_URL}"


#
# Custom settings
#
ENVIRONMENT = "docker"

ELASTIC_APM["SERVICE_NAME"] += " " + ENVIRONMENT


#
# Library settings
#

# django-axes
AXES_BEHIND_REVERSE_PROXY = False
AXES_CACHE = "axes_cache"
