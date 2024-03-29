# Generated by Django 2.2.12 on 2021-01-11 15:53

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_auto_20210111_1649"),
    ]

    operations = [
        migrations.AlterField(
            model_name="objectrecord",
            name="correct",
            field=models.OneToOneField(
                blank=True,
                help_text="Object record which corrects the current record",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="corrected",
                to="core.ObjectRecord",
                verbose_name="correction for",
            ),
        ),
        migrations.AlterField(
            model_name="objectrecord",
            name="end_at",
            field=models.DateField(
                help_text="Legal end date of the object record",
                null=True,
                verbose_name="end at",
            ),
        ),
        migrations.AlterField(
            model_name="objectrecord",
            name="registration_at",
            field=models.DateField(
                default=datetime.date.today,
                help_text="The date when the record was registered in the system",
                verbose_name="registration at",
            ),
        ),
        migrations.AlterField(
            model_name="objectrecord",
            name="start_at",
            field=models.DateField(
                help_text="Legal start date of the object record",
                verbose_name="start at",
            ),
        ),
    ]
