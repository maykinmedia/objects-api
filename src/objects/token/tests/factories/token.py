import factory

from objects.token.models import TokenAuth


class TokenAuthFactory(factory.django.DjangoModelFactory):
    identifier = factory.Sequence(lambda sequence: f"token-{sequence}")
    contact_person = factory.Faker("name")
    email = factory.Faker("email")

    class Meta:
        model = TokenAuth
