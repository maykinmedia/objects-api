from django.db import IntegrityError
from django.test import TestCase

from .factories import ObjectTypeFactory


class ObjectTypeTest(TestCase):
    def test_duplicate_name(self):
        ObjectTypeFactory.create(_name="test")
        with self.assertRaises(IntegrityError):
            ObjectTypeFactory.create(_name="test")
