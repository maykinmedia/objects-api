from django.db import migrations
import uuid


def generate_record_uuids(apps, _):
    ObjectRecord = apps.get_model("core", "ObjectRecord")

    for record in ObjectRecord.objects.all():
        record.uuid = uuid.uuid4()
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_objectrecord_uuid"),
    ]

    operations = [
        migrations.RunPython(generate_record_uuids, migrations.RunPython.noop),
    ]
