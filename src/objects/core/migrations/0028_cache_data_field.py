import logging
from django.db import migrations
from django.db.models import F


logger = logging.getLogger(__name__)


def copy_data_values(apps, _):
    ObjectRecord = apps.get_model("core", "ObjectRecord")
    ObjectRecord.objects.update(_cached_data=F("data"))


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0027_auto_20210920_1602"),
    ]

    operations = [
        migrations.RunPython(copy_data_values, migrations.RunPython.noop),
    ]
