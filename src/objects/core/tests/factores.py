from datetime import date

import factory

from ..models import Object, ObjectRecord


class ObjectFactory(factory.django.DjangoModelFactory):
    object_type = factory.Faker("url")

    class Meta:
        model = Object


class ObjectRecordFactory(factory.django.DjangoModelFactory):
    object = factory.SubFactory(ObjectFactory)
    version = factory.Sequence(lambda n: n)
    data = factory.Sequence(lambda n: {"some_field": n})
    start_at = date.today()

    class Meta:
        model = ObjectRecord
