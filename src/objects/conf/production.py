import os

os.environ.setdefault("ENVIRONMENT", "production")

from .base import *  # noqa isort:skip

#
# Standard Django settings.
#

# Caching sessions.
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Caching templates.
TEMPLATES[0]["OPTIONS"]["loaders"] = [
    ("django.template.loaders.cached.Loader", TEMPLATE_LOADERS)
]

# The file storage engine to use when collecting static files with the
# collectstatic management command.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# Production logging facility.
LOGGING["loggers"].update(
    {
        "django": {
            "handlers": logging_root_handlers,
            "level": "INFO",
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "handlers": logging_root_handlers,
            "level": "CRITICAL",
            "propagate": False,
        },
    }
)

# Only set this when we're behind a reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True  # Sets X-Content-Type-Options: nosniff
SECURE_BROWSER_XSS_FILTER = True  # Sets X-XSS-Protection: 1; mode=block

# Deal with being hosted on a subpath
if subpath and subpath != "/":
    STATIC_URL = f"{subpath}{STATIC_URL}"
    MEDIA_URL = f"{subpath}{MEDIA_URL}"

#
# Custom settings overrides
#
ENVIRONMENT_SHOWN_IN_ADMIN = False
