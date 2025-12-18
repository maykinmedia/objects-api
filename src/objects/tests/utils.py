import os

from requests_mock import Mocker

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


def mock_objecttype(url: str, attrs=None) -> dict:
    attrs = attrs or {}
    response = {
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
        "allowGeometry": True,
        "versions": [
            f"{url}/versions/1",
        ],
    }
    response.update(attrs)
    return response


def mock_objecttypes(uuid1, uuid2):
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "url": f"http://127.0.0.1:8000/api/v2/objecttypes/{uuid1}",
                "uuid": uuid1,
                "name": "Melding",
                "namePlural": "Meldingen",
                "description": "",
                "dataClassification": "intern",
                "maintainerOrganization": "Dimpact",
                "maintainerDepartment": "",
                "contactPerson": "Ad Alarm",
                "contactEmail": "",
                "source": "",
                "updateFrequency": "unknown",
                "providerOrganization": "",
                "documentationUrl": "",
                "labels": {},
                "linkableToZaken": False,
                "createdAt": "2020-12-01",
                "modifiedAt": "2020-12-01",
                "allowGeometry": True,
                "versions": [
                    f"http://127.0.0.1:8000/api/v2/objecttypes/{uuid1}/versions/1",
                    f"http://127.0.0.1:8000/api/v2/objecttypes/{uuid1}/versions/2",
                ],
            },
            {
                "url": f"http://127.0.0.1:8000/api/v2/objecttypes/{uuid2}",
                "uuid": uuid2,
                "name": "Straatverlichting",
                "namePlural": "Straatverlichting",
                "description": "",
                "dataClassification": "open",
                "maintainerOrganization": "Maykin Media",
                "maintainerDepartment": "",
                "contactPerson": "Desiree Lumen",
                "contactEmail": "",
                "source": "",
                "updateFrequency": "unknown",
                "providerOrganization": "",
                "documentationUrl": "",
                "labels": {},
                "linkableToZaken": False,
                "createdAt": "2020-12-01",
                "modifiedAt": "2020-12-01",
                "allowGeometry": True,
                "versions": [
                    f"http://127.0.0.1:8000/api/v2/objecttypes/{uuid2}/versions/1",
                    f"http://127.0.0.1:8000/api/v2/objecttypes/{uuid2}/versions/2",
                ],
            },
        ],
    }


def mock_objecttype_versions(objecttype_uuid: str):
    return {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "url": f"http://127.0.0.1:8000/api/v2/objecttypes/{objecttype_uuid}/versions/2",
                "version": 2,
                "objectType": f"http://127.0.0.1:8000/api/v2/objecttypes/{objecttype_uuid}",
                "status": "published",
                "jsonSchema": {
                    "type": "object",
                    "title": "Tree",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "required": ["description"],
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Explanation what happened",
                        }
                    },
                },
                "createdAt": "2020-11-12",
                "modifiedAt": "2020-11-27",
                "publishedAt": "2020-11-27",
            },
            {
                "url": f"http://127.0.0.1:8000/api/v2/objecttypes/{objecttype_uuid}/versions/1",
                "version": 1,
                "objectType": f"http://127.0.0.1:8000/api/v2/objecttypes/{objecttype_uuid}",
                "status": "published",
                "jsonSchema": {
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
                "createdAt": "2020-12-01",
                "modifiedAt": "2020-12-01",
                "publishedAt": "2020-10-02",
            },
        ],
    }


def mock_objecttype_version(url: str, attrs=None) -> dict:
    attrs = attrs or {}
    response = {
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
    response.update(attrs)
    return response
