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
