import factory.fuzzy


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")

    class Meta:
        model = "accounts.User"
