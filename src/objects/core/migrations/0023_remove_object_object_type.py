# Generated by Django 2.2.12 on 2020-12-22 16:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0022_move_object_types_to_separate_model"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="object",
            name="object_type",
        ),
    ]
