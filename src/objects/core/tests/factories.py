import random
import uuid
from datetime import date, timedelta

from django.contrib.gis.geos import Point

import factory
from factory.fuzzy import BaseFuzzyAttribute
from zgw_consumers.test.factories import ServiceFactory

from ..models import Object, ObjectRecord, ObjectType, ObjectTypeVersion


class ObjectTypeFactory(factory.django.DjangoModelFactory):
    service = factory.SubFactory(ServiceFactory)
    uuid = factory.LazyFunction(uuid.uuid4)
    _name = factory.Faker("word")

    name = factory.Faker("word")
    name_plural = factory.LazyAttribute(lambda x: f"{x.name}s")
    description = factory.Faker("bs")

    class Meta:
        model = ObjectType


class ObjectTypeVersionFactory(factory.django.DjangoModelFactory):
    object_type = factory.SubFactory(ObjectTypeFactory)
    json_schema = {
        "type": "object",
        "title": "Tree",
        "$schema": "http://json-schema.org/draft-07/schema#",
        "required": ["diameter"],
        "properties": {"diameter": {"type": "integer", "description": "size in cm."}},
    }

    class Meta:
        model = ObjectTypeVersion


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0), random.uniform(-90.0, 90.0))


class ObjectDataFactory(factory.DictFactory):
    some_field = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    city = factory.Faker("city")
    description = factory.Faker("sentence")
    diameter = factory.LazyAttribute(lambda x: random.randrange(1, 10_000))


class ObjectFactory(factory.django.DjangoModelFactory):
    object_type = factory.SubFactory(ObjectTypeFactory)

    class Meta:
        model = Object


class ObjectRecordFactory(factory.django.DjangoModelFactory):
    object = factory.SubFactory(ObjectFactory)
    version = factory.Sequence(lambda n: n)
    data = factory.SubFactory(ObjectDataFactory)
    start_at = factory.fuzzy.FuzzyDate(
        start_date=date.today() - timedelta(days=365),
        end_date=date.today(),
    )
    geometry = FuzzyPoint()

    class Meta:
        model = ObjectRecord
