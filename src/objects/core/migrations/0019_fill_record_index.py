from django.db import migrations
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber
from django.db.models import F


def fill_record_index(apps, _):
    ObjectRecord = apps.get_model("core", "ObjectRecord")

    records = ObjectRecord.objects.annotate(
        row_number=Window(
            expression=RowNumber(),
            partition_by=[F("object")],
            order_by=[F("start_at"), F("id")],
        )
    ).order_by("object")

    for record in records:
        if record.index != record.row_number:
            record.index = record.row_number
            record.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_auto_20210113_1239"),
    ]

    operations = [
        migrations.RunPython(fill_record_index, migrations.RunPython.noop),
    ]
