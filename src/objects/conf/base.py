import os

os.environ["_USE_STRUCTLOG"] = "True"

from open_api_framework.conf.base import *  # noqa
from open_api_framework.conf.utils import config

from .api import *  # noqa


DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = config(
    "DB_DISABLE_SERVER_SIDE_CURSORS",
    False,
    help_text=(
        "Whether or not server side cursors should be disabled for Postgres connections. "
        "Setting this to true is required when using a connection pooler in "
        "transaction mode (like PgBouncer). "
        "**WARNING:** the effect of disabling server side cursors on performance has not "
        "been thoroughly tested yet."
    ),
    group="Database",
)

DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# Application definition

INSTALLED_APPS = INSTALLED_APPS + [
    # Optional applications.
    "django.contrib.gis",
    # `django.contrib.sites` added at the project level because it has been removed at the packages level.
    # This component is deprecated and should be completely removed.
    # To determine the project's domain, use the `SITE_DOMAIN` environment variable.
    "django.contrib.sites",
    # External applications.
    "rest_framework_gis",
    # Project applications.
    "objects.accounts",
    "objects.setup_configuration",
    "objects.api",
    "objects.core",
    "objects.token",
    "objects.utils",
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

# FIXME should this be `nl-nl`?
LANGUAGE_CODE = "en-us"
# FIXME should this be UTC?
TIME_ZONE = "Europe/Amsterdam"

#
# Caches
#

OBJECTTYPE_VERSION_CACHE_TIMEOUT = config(
    "OBJECTTYPE_VERSION_CACHE_TIMEOUT",
    default=5 * 60,  # 300 seconds
    help_text="Timeout in seconds for cache when retrieving objecttype versions.",
    group="Cache",
)

#
# Additional Django settings
#


#
# Custom settings
#
PROJECT_NAME = "Objects"
SITE_TITLE = "Starting point"
SHOW_ALERT = True

# Default (connection timeout, read timeout) for the requests library (in seconds)
REQUESTS_DEFAULT_TIMEOUT = (10, 30)

#
# Library settings
#


# Django-Admin-Index
ADMIN_INDEX_DISPLAY_DROP_DOWN_MENU_CONDITION_FUNCTION = (
    "objects.utils.admin_index.should_display_dropdown_menu"
)

#
# MAYKIN-2FA
#
# It uses django-two-factor-auth under the hood so you can configure
# those settings too.
#
# we run the admin site monkeypatch instead.
# Relying Party name for WebAuthn (hardware tokens)
TWO_FACTOR_WEBAUTHN_RP_NAME = "objects api"

# settings for sending notifications
NOTIFICATIONS_KANAAL = "objecten"

CELERY_RESULT_EXPIRES = config(
    "CELERY_RESULT_EXPIRES",
    3600,
    help_text=(
        "How long the results of tasks will be stored in Redis (in seconds),"
        " this can be set to a lower duration to lower memory usage for Redis."
    ),
    group="Celery",
)

# Add (by default) 5 (soft), 15 (hard) minute timeouts to all Celery tasks.
CELERY_TASK_TIME_LIMIT = config(
    "CELERY_TASK_HARD_TIME_LIMIT",
    default=15 * 60,
    help_text=(
        "Task hard time limit in seconds. The worker processing the task will be "
        "killed and replaced with a new one when this is exceeded."
    ),
    group="Celery",
)  # hard

#
# Django setup configuration
#
SETUP_CONFIGURATION_STEPS = (
    "django_setup_configuration.contrib.sites.steps.SitesConfigurationStep",
    "zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep",
    "notifications_api_common.contrib.setup_configuration.steps.NotificationConfigurationStep",
    "mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep",
    "objects.setup_configuration.steps.objecttypes.ObjectTypesConfigurationStep",
    "objects.setup_configuration.steps.token_auth.TokenAuthConfigurationStep",
)

NOTIFICATIONS_API_GET_DOMAIN = "objects.utils.get_domain"

#
# DJANGO-STRUCTLOG
#
DJANGO_STRUCTLOG_IP_LOGGING_ENABLED = False
DJANGO_STRUCTLOG_CELERY_ENABLED = True
