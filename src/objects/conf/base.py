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
    "objects.config",
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
    "zgw_consumers.contrib.setup_configuration.steps.ServiceConfigurationStep",
    "objects.config.objecttypes.ObjectTypesStep",
)


#
# Objecttypes settings
#

# setup_configuration command
# sites config
SITES_CONFIG_ENABLE = config("SITES_CONFIG_ENABLE", default=False, add_to_docs=False)
OBJECTS_DOMAIN = config("OBJECTS_DOMAIN", "", add_to_docs=False)
OBJECTS_ORGANIZATION = config("OBJECTS_ORGANIZATION", "", add_to_docs=False)
# objecttypes config
OBJECTS_OBJECTTYPES_CONFIG_ENABLE = config(
    "OBJECTS_OBJECTTYPES_CONFIG_ENABLE", default=False, add_to_docs=False
)
OBJECTTYPES_API_ROOT = config("OBJECTTYPES_API_ROOT", "", add_to_docs=False)
if OBJECTTYPES_API_ROOT and not OBJECTTYPES_API_ROOT.endswith("/"):
    OBJECTTYPES_API_ROOT = f"{OBJECTTYPES_API_ROOT.strip()}/"
OBJECTTYPES_API_OAS = config(
    "OBJECTTYPES_API_OAS",
    default=f"{OBJECTTYPES_API_ROOT}schema/openapi.yaml",
    add_to_docs=False,
)
OBJECTS_OBJECTTYPES_TOKEN = config("OBJECTS_OBJECTTYPES_TOKEN", "", add_to_docs=False)
# Demo User Configuration
DEMO_CONFIG_ENABLE = config("DEMO_CONFIG_ENABLE", default=False, add_to_docs=False)
DEMO_TOKEN = config("DEMO_TOKEN", "", add_to_docs=False)
DEMO_PERSON = config("DEMO_PERSON", "", add_to_docs=False)
DEMO_EMAIL = config("DEMO_EMAIL", "", add_to_docs=False)
