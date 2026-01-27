import uuid

from django.core.management import CommandError, call_command
from django.test import TestCase

import requests_mock
from freezegun import freeze_time
from zgw_consumers.models import Service

from objects.core.models import ObjectType, ObjectTypeVersion
from objects.core.tests.factories import ObjectTypeFactory
from objects.tests.utils import (
    mock_objecttype_versions,
    mock_objecttypes,
)


@freeze_time("2020-12-01")
class TestImportObjectTypesCommand(TestCase):
    def setUp(self):
        super().setUp()
        self.url = "http://127.0.0.1:8000/api/v2/"

        self.m = requests_mock.Mocker()
        self.m.start()

        self.service = Service.objects.create(api_root=self.url, slug="objecttypes-api")
        self.m.head(self.url, status_code=200, headers={"api-version": "2.2.2"})

    def tearDown(self):
        self.m.stop()

    def _call_command(self):
        call_command("import_objecttypes", self.service.slug)

    def test_api_version_is_required(self):
        self.m.head(self.url, status_code=200)

        with self.assertRaisesMessage(
            CommandError, "API version must be 2.2.2 or higher"
        ):
            self._call_command()

    def test_api_version_must_be_greater_than_constant(self):
        self.m.head(self.url, status_code=200, headers={"api-version": "2.2.1"})

        with self.assertRaisesMessage(
            CommandError, "API version must be 2.2.2 or higher"
        ):
            self._call_command()

    def test_command_fails_if_http_error(self):
        self.m.get(f"{self.url}objecttypes", status_code=404)
        with self.assertRaises(CommandError):
            self._call_command()

    def test_new_objecttypes_are_created(self):
        self.assertEqual(ObjectType.objects.count(), 0)
        self.assertEqual(ObjectTypeVersion.objects.count(), 0)

        uuid1 = str(uuid.uuid4())
        uuid2 = str(uuid.uuid4())

        self.m.get(f"{self.url}objecttypes", json=mock_objecttypes(uuid1, uuid2))
        self.m.get(
            f"{self.url}objecttypes/{uuid1}/versions",
            json=mock_objecttype_versions(uuid1),
        )
        self.m.get(
            f"{self.url}objecttypes/{uuid2}/versions",
            json=mock_objecttype_versions(uuid2),
        )

        self._call_command()

        self.assertEqual(ObjectType.objects.count(), 2)

        objecttype = ObjectType.objects.get(uuid=uuid1)
        self.assertEqual(objecttype.name, "Melding")
        self.assertEqual(objecttype.name_plural, "Meldingen")
        self.assertEqual(objecttype.description, "")
        self.assertEqual(objecttype.data_classification, "intern")
        self.assertEqual(objecttype.maintainer_organization, "Dimpact")
        self.assertEqual(objecttype.maintainer_department, "")
        self.assertEqual(objecttype.contact_person, "Ad Alarm")
        self.assertEqual(objecttype.contact_email, "")
        self.assertEqual(objecttype.source, "")
        self.assertEqual(objecttype.update_frequency, "unknown")
        self.assertEqual(objecttype.provider_organization, "")
        self.assertEqual(objecttype.documentation_url, "")
        self.assertEqual(objecttype.labels, {})
        self.assertEqual(objecttype.linkable_to_zaken, False)
        self.assertEqual(str(objecttype.created_at), "2020-12-01")
        self.assertEqual(str(objecttype.modified_at), "2020-12-01")
        self.assertEqual(objecttype.allow_geometry, True)

        self.assertEqual(ObjectTypeVersion.objects.count(), 4)

        version = ObjectTypeVersion.objects.get(object_type=objecttype, version=1)
        self.assertEqual(str(version.created_at), "2020-12-01")
        self.assertEqual(str(version.modified_at), "2020-12-01")
        self.assertEqual(str(version.published_at), "2020-10-02")
        self.assertEqual(
            version.json_schema,
            {
                "type": "object",
                "title": "Melding",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "required": ["description"],
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Explanation what happened",
                    }
                },
            },
        )
        self.assertEqual(str(version.status), "published")

    def test_existing_objecttypes_are_updated(self):
        objecttype1 = ObjectTypeFactory.create()
        objecttype2 = ObjectTypeFactory.create()

        self.m.get(
            f"{self.url}objecttypes",
            json=mock_objecttypes(str(objecttype1.uuid), str(objecttype2.uuid)),
        )
        self.m.get(
            f"{self.url}objecttypes/{str(objecttype1.uuid)}/versions",
            json=mock_objecttype_versions(str(objecttype1.uuid)),
        )
        self.m.get(
            f"{self.url}objecttypes/{str(objecttype2.uuid)}/versions",
            json=mock_objecttype_versions(str(objecttype2.uuid)),
        )

        self._call_command()
        self.assertEqual(ObjectType.objects.count(), 2)
        self.assertEqual(ObjectTypeVersion.objects.count(), 4)

        objecttype = ObjectType.objects.get(uuid=objecttype1.uuid)
        self.assertEqual(objecttype.name, "Melding")

        version = ObjectTypeVersion.objects.get(object_type=objecttype, version=1)
        self.assertEqual(
            version.json_schema,
            {
                "type": "object",
                "title": "Melding",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "required": ["description"],
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "Explanation what happened",
                    }
                },
            },
        )
