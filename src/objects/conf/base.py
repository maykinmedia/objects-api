from pathlib import Path

import structlog
from open_api_framework.conf.base import *  # noqa
from open_api_framework.conf.utils import config

from .api import *  # noqa

DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"
DATABASES["default"]["CONN_MAX_AGE"] = config(
    "DB_CONN_MAX_AGE",
    default=0,
    help_text=(
        "The lifetime of a database connection, as an integer of seconds. "
        "Use 0 to close database connections at the end of each request — Django’s historical behavior. "
        "This setting cannot be set in combination with connection pooling."
    ),
    group="Database",
)


# https://docs.djangoproject.com/en/5.2/ref/databases/#connection-pool
# https://www.psycopg.org/psycopg3/docs/api/pool.html#the-connectionpool-class

DB_POOL_ENABLED = config(
    "DB_POOL_ENABLED",
    default=False,
    help_text=("Whether to use connection pooling."),
    group="Database",
)

DB_POOL_MIN_SIZE = config(
    "DB_POOL_MIN_SIZE",
    default=4,
    help_text=(
        "The minimum number of connection the pool will hold. "
        "The pool will actively try to create new connections if some are lost (closed, broken) "
        "and will try to never go below min_size."
    ),
    group="Database",
)

DB_POOL_MAX_SIZE = config(
    "DB_POOL_MAX_SIZE",
    default=None,
    help_text=(
        "The maximum number of connections the pool will hold. "
        "If None, or equal to min_size, the pool will not grow or shrink. "
        "If larger than min_size, the pool can grow if more than min_size connections "
        "are requested at the same time and will shrink back after the extra connections "
        "have been unused for more than max_idle seconds."
    ),
    group="Database",
)

DB_POOL_TIMEOUT = config(
    "DB_POOL_TIMEOUT",
    default=30,
    help_text=(
        "The default maximum time in seconds that a client can wait "
        "to receive a connection from the pool (using connection() or getconn()). "
        "Note that these methods allow to override the timeout default."
    ),
    group="Database",
)

DB_POOL_MAX_WAITING = config(
    "DB_POOL_MAX_WAITING",
    default=0,
    help_text=(
        "Maximum number of requests that can be queued to the pool, "
        "after which new requests will fail, raising TooManyRequests. 0 means no queue limit."
    ),
    group="Database",
)

DB_POOL_MAX_LIFETIME = config(
    "DB_POOL_MAX_LIFETIME",
    default=60 * 60,
    help_text=(
        "The maximum lifetime of a connection in the pool, in seconds. "
        "Connections used for longer get closed and replaced by a new one. "
        "The amount is reduced by a random 10% to avoid mass eviction"
    ),
    group="Database",
)

DB_POOL_MAX_IDLE = config(
    "DB_POOL_MAX_IDLE",
    default=10 * 60,
    help_text=(
        "Maximum time, in seconds, that a connection can stay unused in the pool "
        "before being closed, and the pool shrunk. This only happens to "
        "connections more than min_size, if max_size allowed the pool to grow."
    ),
    group="Database",
)

DB_POOL_RECONNECT_TIMEOUT = config(
    "DB_POOL_RECONNECT_TIMEOUT",
    default=5 * 60,
    help_text=(
        "Maximum time, in seconds, the pool will try to create a connection. "
        "If a connection attempt fails, the pool will try to reconnect a few times, "
        "using an exponential backoff and some random factor to avoid mass attempts. "
        "If repeated attempts fail, after reconnect_timeout second the connection "
        "attempt is aborted and the reconnect_failed() callback invoked."
    ),
    group="Database",
)

DB_POOL_NUM_WORKERS = config(
    "DB_POOL_NUM_WORKERS",
    default=3,
    help_text=(
        "Number of background worker threads used to maintain the pool state. "
        "Background workers are used for example to create new connections and "
        "to clean up connections when they are returned to the pool."
    ),
    group="Database",
)


if DB_POOL_ENABLED:
    DATABASES["default"]["OPTIONS"] = {
        "pool": {
            "min_size": DB_POOL_MIN_SIZE,
            "max_size": DB_POOL_MAX_SIZE,
            "timeout": DB_POOL_TIMEOUT,
            "max_waiting": DB_POOL_MAX_WAITING,
            "max_lifetime": DB_POOL_MAX_LIFETIME,
            "max_idle": DB_POOL_MAX_IDLE,
            "reconnect_timeout": DB_POOL_RECONNECT_TIMEOUT,
            "num_workers": DB_POOL_NUM_WORKERS,
        }
    }

# Application definition

INSTALLED_APPS = INSTALLED_APPS + [
    # Optional applications.
    "django.contrib.gis",
    "django_structlog",
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

# XXX: this should be renamed to `LOG_REQUESTS` in the next major release
_log_requests_via_middleware = config(
    "ENABLE_STRUCTLOG_REQUESTS",
    default=True,
    help_text=("enable structured logging of requests"),
    group="Logging",
)
if _log_requests_via_middleware:
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
        "django_structlog.middlewares.RequestMiddleware",
    )

# TODO move this back to OAF
# Override LOGGING, because OAF does not yet apply structlog for all components
logging_root_handlers = ["console"] if LOG_STDOUT else ["json_file"]
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # structlog - foreign_pre_chain handles logs coming from stdlib logging module,
        # while the `structlog.configure` call handles everything coming from structlog.
        # They are mutually exclusive.
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": [
                structlog.contextvars.merge_contextvars,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
            ],
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "foreign_pre_chain": [
                structlog.contextvars.merge_contextvars,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
            ],
        },
        "verbose": {
            "format": "%(asctime)s %(levelname)s %(name)s %(module)s %(process)d %(thread)d  %(message)s"
        },
        "timestamped": {"format": "%(asctime)s %(levelname)s %(name)s  %(message)s"},
        "simple": {"format": "%(levelname)s  %(message)s"},
        "performance": {"format": "%(asctime)s %(process)d | %(thread)d | %(message)s"},
        "db": {"format": "%(asctime)s | %(message)s"},
        "outgoing_requests": {"()": HttpFormatter},
    },
    # TODO can be removed?
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
    },
    "handlers": {
        # TODO can be removed?
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": config(
                "LOG_FORMAT_CONSOLE",
                default="json",
                help_text=(
                    "The format for the console logging handler, possible options: ``json``, ``plain_console``."
                ),
                group="Logging",
            ),
        },
        "console_db": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "db",
        },
        # replaces the "django" and "project" handlers - in containerized applications
        # the best practices is to log to stdout (use the console handler).
        "json_file": {
            "level": LOG_LEVEL,  # always debug might be better?
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGGING_DIR) / "application.jsonl",
            "formatter": "json",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
        },
        "performance": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGGING_DIR) / "performance.log",
            "formatter": "performance",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
        },
        "requests": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGGING_DIR) / "requests.log",
            "formatter": "timestamped",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 10,
        },
        "log_outgoing_requests": {
            "level": "DEBUG",
            "formatter": "outgoing_requests",
            "class": "logging.StreamHandler",  # to write to stdout
        },
        "save_outgoing_requests": {
            "level": "DEBUG",
            # enabling saving to database
            "class": "log_outgoing_requests.handlers.DatabaseOutgoingRequestsHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": logging_root_handlers,
            "level": "ERROR",
            "propagate": False,
        },
        PROJECT_DIRNAME: {
            "handlers": logging_root_handlers,
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "mozilla_django_oidc": {
            "handlers": logging_root_handlers,
            "level": LOG_LEVEL,
        },
        f"{PROJECT_DIRNAME}.utils.middleware": {
            "handlers": logging_root_handlers,
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "vng_api_common": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["console_db"] if LOG_QUERIES else [],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.request": {
            "handlers": logging_root_handlers,
            "level": LOG_LEVEL,
            "propagate": False,
        },
        # suppress django.server request logs because those are already emitted by
        # django-structlog middleware
        "django.server": {
            "handlers": ["console"],
            "level": "WARNING" if _log_requests_via_middleware else "INFO",
            "propagate": False,
        },
        "django.template": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "log_outgoing_requests": {
            "handlers": (
                ["log_outgoing_requests", "save_outgoing_requests"]
                if LOG_REQUESTS
                else []
            ),
            "level": "DEBUG",
            "propagate": True,
        },
        "django_structlog": {
            "handlers": logging_root_handlers,
            "level": "INFO",
            "propagate": False,
        },
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        # structlog.processors.ExceptionPrettyPrinter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


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
