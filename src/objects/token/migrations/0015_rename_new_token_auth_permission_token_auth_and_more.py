# Generated by Django 4.2.11 on 2024-05-02 10:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0028_alter_objectrecord_data"),
        ("token", "0014_alter_permission_unique_together_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="permission",
            old_name="new_token_auth",
            new_name="token_auth",
        ),
        migrations.AlterUniqueTogether(
            name="permission",
            unique_together={("token_auth", "object_type")},
        ),
    ]
