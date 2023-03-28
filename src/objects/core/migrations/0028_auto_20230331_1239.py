# Generated by Django 2.2.28 on 2023-03-31 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0027_auto_20211203_1209"),
    ]

    operations = [
        migrations.AlterField(
            model_name="objectrecord",
            name="end_at",
            field=models.DateField(
                help_text="Legal end date of the object record (exclusive)",
                null=True,
                verbose_name="end at",
            ),
        ),
        migrations.AlterField(
            model_name="objectrecord",
            name="start_at",
            field=models.DateField(
                help_text="Legal start date of the object record (inclusive)",
                verbose_name="start at",
            ),
        ),
    ]