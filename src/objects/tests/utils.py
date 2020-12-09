import logging
import os

from requests_mock import Mocker

logger = logging.getLogger(__name__)

MOCK_FILES_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "schemas",
)

_cache = {}


def read_schema(service: str):
    if service not in _cache:
        file_name = f"{service}.yaml"
        file = os.path.join(MOCK_FILES_DIR, file_name)
        with open(file, "rb") as api_spec:
            _cache[service] = api_spec.read()

    return _cache[service]


def mock_service_oas_get(m: Mocker, url: str, service: str, oas_url: str = "") -> None:
    if not oas_url:
        oas_url = f"{url}schema/openapi.yaml?v=3"
    content = read_schema(service)
    m.get(oas_url, content=content)


def mock_objecttype(url: str) -> dict:
    return {
        "url": url,
        "name": "Boom",
        "namePlural": "Bomen",
        "description": "",
        "dataClassification": "open",
        "maintainerOrganization": "Gemeente Delft",
        "maintainerDepartment": "",
        "contactPerson": "Jan Eik",
        "contactEmail": "",
        "source": "",
        "updateFrequency": "unknown",
        "providerOrganization": "",
        "documentationUrl": "",
        "labels": {},
        "createdAt": "2020-12-01",
        "modifiedAt": "2020-12-01",
        "versions": [
            f"{url}/versions/1",
        ],
    }


def mock_objecttype_version(url: str) -> dict:
    return {
        "url": f"{url}/versions/1",
        "version": 1,
        "objectType": url,
        "status": "published",
        "jsonSchema": {
            "type": "object",
            "title": "Tree",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "required": ["diameter"],
            "properties": {
                "diameter": {"type": "integer", "description": "Size in cm."},
                "plantDate": {
                    "type": "string",
                    "format": "date",
                    "description": "Date the tree was planted.",
                },
            },
        },
        "createdAt": "2020-11-14",
        "modifiedAt": "2020-11-16",
        "publishedAt": "2020-11-16",
    }
