from django.contrib.auth import get_user_model

import factory
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = User

    class Params:
        superuser = factory.Trait(
            is_staff=True,
            is_superuser=True,
        )


class StaffUserFactory(UserFactory):
    is_staff = True
