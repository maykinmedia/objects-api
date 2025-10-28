from django.test import TestCase

from ..models import ObjectRecord
from .factories import ObjectFactory, ObjectTypeFactory


class ObjectRecordTestCase(TestCase):
    def test_object_type_is_denormalized_on_object_record(self):
        object_type1 = ObjectTypeFactory.create()
        object = ObjectFactory.create(object_type=object_type1)

        record = ObjectRecord.objects.create(
            object=object, version=1, start_at="2025-01-01"
        )

        self.assertEqual(record._object_type, object_type1)
