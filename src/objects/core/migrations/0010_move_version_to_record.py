from django.db import migrations
from datetime import date


def move_vesrion_to_record(apps, _):
    Object = apps.get_model("core", "Object")
    ObjectRecord = apps.get_model("core", "ObjectRecord")

    for object in Object.objects.all():
        ObjectRecord.objects.filter(object=object).update(version=object.version)


def move_version_from_record(apps, _):
    Object = apps.get_model("core", "Object")

    for object in Object.objects.all():
        object.version = object.last_record.version
        object.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_objectrecord_version"),
    ]

    operations = [
        migrations.RunPython(move_vesrion_to_record, move_version_from_record),
    ]
