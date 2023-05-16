from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from objects.core.admin import ObjectRecord, ObjectRecordInline


class ObjectRecordInlineTestCase(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.inline = ObjectRecordInline(ObjectRecord, self.site)

    def test_get_data_display(self):
        obj = ObjectRecord(data={"foo": "bar"})
        self.assertEqual(self.inline.get_data_display(obj), '{\n    "foo": "bar"\n}')
