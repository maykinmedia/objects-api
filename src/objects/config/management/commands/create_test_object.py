from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.urls import reverse

import requests


class Command(BaseCommand):
    help = "Create a test object as an integration test for Objects and Objecttypes API"

    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--keep-data",
            dest="keep_data",
            action="store_true",
            help="The component name to define urlconf and schema info",
        )

    def handle(self, **options):
        # For test purposes the same DEMO_TOKEN is used for both Objects API and Objecttypes API
        if not settings.DEMO_TOKEN:
            raise CommandError("DEMO_TOKEN env var should be configured")

        req = requests.session()
        req.headers.update(
            {
                "Authorization": f"Token {settings.DEMO_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Content-Crs": "EPSG:4326",
            }
        )
        req.hooks = {"response": [lambda r, *args, **kwargs: r.raise_for_status()]}

        # 1. create an Object Type
        objecttype_data = {
            "name": "boom",
            "namePlural": "bomen",
            "description": "tree type description",
        }
        objecttypes_list_url = "http://localhost:8001/api/v2/objecttypes"
        response = req.post(objecttypes_list_url, json=objecttype_data)

        objecttype_url = response.json()["url"]
        objecttype_uuid = response.json()["uuid"]
        self.stdout.write(f"Demo objecttype {objecttype_url} was created")

        # 2. Create an Object Type version
        objectversion_data = {
            "status": "draft",
            "jsonSchema": {
                "type": "object",
                "title": "Tree",
                "$schema": "http://json-schema.org/draft-07/schema#",
                "required": ["diameter"],
                "properties": {
                    "diameter": {"type": "integer", "description": "size in cm."}
                },
            },
        }
        objectversion_list_url = (
            f"http://localhost:8001/api/v2/objecttypes/{objecttype_uuid}/versions"
        )
        response = req.post(objectversion_list_url, json=objectversion_data)

        objectversion_url = response.json()["url"]
        objectversion_version = response.json()["version"]
        self.stdout.write(f"Demo objectversion {objectversion_url} was created")

        # 3. Create an Object
        object_data = {
            "type": objecttype_url.replace("localhost:8001", "objecttypes:8000"),
            "record": {
                "typeVersion": objectversion_version,
                "data": {"diameter": 30},
                "startAt": "2024-01-01",
            },
        }
        object_list_url = "http://localhost:8000/api/v2/objects"
        response = req.post(object_list_url, json=object_data)

        object_url = response.json()["url"]
        self.stdout.write(f"Demo object {object_url} was created")

        if options["keep_data"]:
            self.stdout.write("Demo objecttype and object are remained in DB")
            return

        # 4. Delete an Object
        req.delete(object_url)
        self.stdout.write(f"Demo object {object_url} was deleted")

        # 5. Delete an Object Version
        req.delete(objectversion_url)
        self.stdout.write(f"Demo objectversion {objectversion_url} was deleted")

        # 6. Delete an Object Type
        req.delete(objecttype_url)
        self.stdout.write(f"Demo objecttype {objecttype_url} was deleted")

        self.stdout.write(self.style.SUCCESS("Demo process is finished"))
