"""
Staging environment settings module.
This *should* be nearly identical to production.
"""
import os

os.environ.setdefault("ENVIRONMENT", "staging")

from .production import *  # noqa
