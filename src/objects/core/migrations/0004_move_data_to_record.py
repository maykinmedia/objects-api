from django.db import migrations
from datetime import date
from ..constants import RecordType


def move_data_to_record(apps, _):
    Object = apps.get_model("core", "Object")
    ObjectRecord = apps.get_model("core", "ObjectRecord")

    for object in Object.objects.all():
        ObjectRecord.objects.create(
            object=object, registration_date=date.today(), data=object.data
        )


def move_data_from_record(apps, _):
    ObjectRecord = apps.get_model("core", "ObjectRecord")

    for record in ObjectRecord.objects.filter(record_type=RecordType.created):
        object = record.object
        object.data = record.data
        object.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_objectrecord"),
    ]

    operations = [
        migrations.RunPython(move_data_to_record, move_data_from_record),
    ]
