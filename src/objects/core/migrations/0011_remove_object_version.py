# Generated by Django 2.2.12 on 2020-09-15 12:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_move_version_to_record"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="object",
            name="version",
        ),
    ]
