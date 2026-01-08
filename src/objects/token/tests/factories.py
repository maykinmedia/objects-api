import factory

from objects.core.tests.factories import ObjectTypeFactory

from ..constants import PermissionModes
from ..models import Permission, TokenAuth


class TokenAuthFactory(factory.django.DjangoModelFactory[TokenAuth]):
    identifier = factory.Sequence(lambda sequence: f"token-{sequence}")
    contact_person = factory.Faker("name")
    email = factory.Faker("email")

    class Meta:
        model = TokenAuth


class PermissionFactory(factory.django.DjangoModelFactory[Permission]):
    token_auth = factory.SubFactory(TokenAuthFactory)
    object_type = factory.SubFactory(ObjectTypeFactory)
    mode = PermissionModes.read_and_write

    class Meta:
        model = Permission
