from django.db import migrations


def remove_objects_with_empty_object_type(apps, _):
    Object = apps.get_model("core", "Object")
    # these objects are logged in 0022_move_object_types_to_separate_model
    Object.objects.filter(object_type__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0024_auto_20201222_1811"),
    ]

    operations = [
        migrations.RunPython(
            remove_objects_with_empty_object_type, migrations.RunPython.noop
        ),
    ]
