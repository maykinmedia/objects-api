import factory
import factory.fuzzy

from objects.core.tests.factories import ObjectTypeFactory

from ..constants import PermissionModes


class TokenAuthFactory(factory.django.DjangoModelFactory):
    identifier = factory.Sequence(lambda sequence: f"token-{sequence}")
    contact_person = factory.Faker("name")
    email = factory.Faker("email")

    class Meta:
        model = "token.TokenAuth"


class PermissionFactory(factory.django.DjangoModelFactory):
    token_auth = factory.SubFactory(TokenAuthFactory)
    object_type = factory.SubFactory(ObjectTypeFactory)
    mode = PermissionModes.read_and_write

    class Meta:
        model = "token.Permission"
