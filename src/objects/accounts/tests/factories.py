import factory
import factory.fuzzy

from ..constants import PermissionModes


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")

    class Meta:
        model = "accounts.User"


class ObjectPermissionFactory(factory.django.DjangoModelFactory):
    object_type = factory.Faker("url")
    mode = factory.fuzzy.FuzzyChoice(choices=PermissionModes.values)

    class Meta:
        model = "accounts.ObjectPermission"

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        # optional M2M, do nothing when no arguments are passed
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)
