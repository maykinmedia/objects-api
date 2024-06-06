from open_api_framework.conf.base import *  # noqa
from open_api_framework.conf.utils import config

from .api import *  # noqa

init_sentry()


DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": config("DB_NAME", "objects"),
        "USER": config("DB_USER", "objects"),
        "PASSWORD": config("DB_PASSWORD", "objects"),
        "HOST": config("DB_HOST", "localhost"),
        "PORT": config("DB_PORT", 5432),
    }
}


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


# VNG API Common
CUSTOM_CLIENT_FETCHER = "objects.utils.client.get_client"

# settings for sending notifications
NOTIFICATIONS_KANAAL = "objecten"
NOTIFICATIONS_DISABLED = config("NOTIFICATIONS_DISABLED", False)

# TODO should this be moved to open-api-framework?
# Add (by default) 5 (soft), 15 (hard) minute timeouts to all Celery tasks.
CELERY_TASK_TIME_LIMIT = config("CELERY_TASK_HARD_TIME_LIMIT", default=15 * 60)  # hard
CELERY_TASK_SOFT_TIME_LIMIT = config(
    "CELERY_TASK_SOFT_TIME_LIMIT", default=5 * 60
)  # soft

#
# Django setup configuration
#
SETUP_CONFIGURATION_STEPS = [
    "objects.config.site.SiteConfigurationStep",
    "objects.config.objecttypes.ObjecttypesStep",
    "objects.config.demo.DemoUserStep",
]


#
# Objecttypes settings
#

# setup_configuration command
# sites config
SITES_CONFIG_ENABLE = config("SITES_CONFIG_ENABLE", default=True)
OBJECTS_DOMAIN = config("OBJECTS_DOMAIN", "")
OBJECTS_ORGANIZATION = config("OBJECTS_ORGANIZATION", "")
# objecttypes config
OBJECTS_OBJECTTYPES_CONFIG_ENABLE = config(
    "OBJECTS_OBJECTTYPES_CONFIG_ENABLE", default=True
)
OBJECTTYPES_API_ROOT = config("OBJECTTYPES_API_ROOT", "")
if OBJECTTYPES_API_ROOT and not OBJECTTYPES_API_ROOT.endswith("/"):
    OBJECTTYPES_API_ROOT = f"{OBJECTTYPES_API_ROOT.strip()}/"
OBJECTTYPES_API_OAS = config(
    "OBJECTTYPES_API_OAS", default=f"{OBJECTTYPES_API_ROOT}schema/openapi.yaml"
)
OBJECTS_OBJECTTYPES_TOKEN = config("OBJECTS_OBJECTTYPES_TOKEN", "")
# Demo User Configuration
DEMO_CONFIG_ENABLE = config("DEMO_CONFIG_ENABLE", default=DEBUG)
DEMO_TOKEN = config("DEMO_TOKEN", "")
DEMO_PERSON = config("DEMO_PERSON", "")
DEMO_EMAIL = config("DEMO_EMAIL", "")
