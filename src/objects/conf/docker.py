import os

from open_api_framework.conf.utils import config

os.environ.setdefault("DB_USER", config("DB_USER", "objects"))
os.environ.setdefault("DB_NAME", config("DB_NAME", "objects"))
os.environ.setdefault("DB_PASSWORD", config("DB_PASSWORD", "objects"))
os.environ.setdefault("DB_HOST", config("DB_HOST", "db"))
os.environ.setdefault("ENVIRONMENT", "docker")
os.environ.setdefault("LOG_STDOUT", "yes")
os.environ.setdefault("LOG_FORMAT_CONSOLE", "json")

from .production import *  # noqa isort:skip
