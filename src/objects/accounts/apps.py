import os
import sys

from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.db.models.signals import post_migrate


def update_admin_index(sender, **kwargs):
    from django_admin_index.models import AppGroup

    AppGroup.objects.all().delete()

    # Make sure Objects models are registered.
    for app in settings.INSTALLED_APPS:
        if app.startswith("objects"):
            app_config = apps.get_app_config(app.split(".")[-1])
            create_contenttypes(app_config)

    call_command("loaddata", "default_admin_index", verbosity=0)


def create_superuser(sender, **kwargs):
    if "test" in sys.argv:
        return

    username = os.getenv("SUPERUSER_NAME")
    password = os.getenv("SUPERUSER_PASSWORD")

    if username and password:
        call_command("createinitialsuperuser", username, password=password)


class AccountsConfig(AppConfig):
    name = "objects.accounts"

    def ready(self):
        post_migrate.connect(update_admin_index, sender=self)
        post_migrate.connect(create_superuser, sender=self)
