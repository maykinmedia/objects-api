from .factories import ObjectTypeFactory
from django.test import TestCase
from django.db import IntegrityError

class ObjectTypeTest(TestCase):
    def test_duplicate_name(self):
        ObjectTypeFactory.create(_name="test")
        with self.assertRaises(IntegrityError):
            ObjectTypeFactory.create(_name="test")