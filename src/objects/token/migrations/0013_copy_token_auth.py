from django.db import migrations


def switch_to_new_token_model(apps, _):
    OldTokenAuth = apps.get_model("token", "OldTokenAuth")
    TokenAuth = apps.get_model("token", "TokenAuth")

    for old_token in OldTokenAuth.objects.all():
        token, created = TokenAuth.objects.get_or_create(
            token=old_token.token,
            defaults={
                "contact_person": old_token.contact_person,
                "email": old_token.email,
                "organization": old_token.organization,
                "last_modified": old_token.last_modified,
                "created": old_token.created,
                "application": old_token.application,
                "administration": old_token.administration,
                "is_superuser": old_token.is_superuser,
            },
        )

        # add fk relations to new model
        if created:
            old_token.permissions.all().update(new_token_auth=token)


def switch_to_old_token_model(apps, _):
    OldTokenAuth = apps.get_model("token", "OldTokenAuth")
    TokenAuth = apps.get_model("token", "TokenAuth")

    # copy tokens to old model
    for token in TokenAuth.objects.all():
        old_token, created = OldTokenAuth.objects.get_or_create(
            token=token.token,
            defaults={
                "contact_person": token.contact_person,
                "email": token.email,
                "organization": token.organization,
                "last_modified": token.last_modified,
                "created": token.created,
                "application": token.application,
                "administration": token.administration,
                "is_superuser": token.is_superuser,
            },
        )

        # add fk relations to old model
        if created:
            token.permissions.all().update(old_token_auth=old_token)


class Migration(migrations.Migration):
    dependencies = [
        ("token", "0012_tokenauth_permission_token_auth"),
    ]

    operations = [
        migrations.RunPython(switch_to_new_token_model, switch_to_old_token_model),
    ]
