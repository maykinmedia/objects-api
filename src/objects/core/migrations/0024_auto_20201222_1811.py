# Generated by Django 2.2.12 on 2020-12-22 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_remove_object_object_type"),
    ]

    operations = [
        migrations.RenameField(
            model_name="object",
            old_name="object_type_fk",
            new_name="object_type",
        ),
    ]