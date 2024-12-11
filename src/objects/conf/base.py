from open_api_framework.conf.base import *  # noqa
from open_api_framework.conf.utils import config

from .api import *  # noqa

init_sentry()

DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"


# Application definition

INSTALLED_APPS = INSTALLED_APPS + [
    # Optional applications.
    "django.contrib.gis",
    # External applications.
    "rest_framework_gis",
    # Project applications.
    "objects.accounts",
    "objects.api",
    "objects.setup_configuration",
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
# Additional Django settings
#


#
# Custom settings
#
PROJECT_NAME = "Objects"
SITE_TITLE = "Starting point"
SHOW_ALERT = True

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
    "objects.setup_configuration.steps.token_auth.TokenAuthConfigurationStep",
    "objects.setup_configuration.steps.sites.SitesConfigurationStep",
    "objects.setup_configuration.steps.objecttypes.ObjectTypesConnectionConfigurationStep",
)
