# Generated by Django 2.2.12 on 2020-09-15 15:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_generate_record_uuids"),
    ]

    operations = [
        migrations.AlterField(
            model_name="objectrecord",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, help_text="Unique identifier (UUID4)", unique=True
            ),
        ),
    ]
