import uuid
from datetime import date

import factory
from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service

from ..models import Object, ObjectRecord, ObjectType


class ServiceFactory(factory.django.DjangoModelFactory):
    label = factory.Faker("word")
    api_root = factory.Faker("url")
    api_type = APITypes.orc
    auth_type = AuthTypes.no_auth

    class Meta:
        model = Service


class ObjectTypeFactory(factory.django.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    uuid = factory.LazyFunction(uuid.uuid4)
    _name = factory.Faker("word")

    class Meta:
        model = ObjectType


class ObjectFactory(factory.django.DjangoModelFactory):
    object_type = factory.SubFactory(ObjectTypeFactory)

    class Meta:
        model = Object


class ObjectRecordFactory(factory.django.DjangoModelFactory):
    object = factory.SubFactory(ObjectFactory)
    version = factory.Sequence(lambda n: n)
    data = factory.Sequence(lambda n: {"some_field": n})
    start_at = date.today()

    class Meta:
        model = ObjectRecord
