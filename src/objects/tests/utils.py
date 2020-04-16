import requests_mock


def mock_objecttype(m: requests_mock.Mocker, url: str) -> dict:
    return {
        "url": url,
        "name": "boom",
        "namePlural": "bomen",
        "versions": [
            {
                "version": 1,
                "publicationDate": "2020-03-01",
                "jsonSchema": {
                    "title": "Tree",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "required": ["diameter"],
                    "properties": {
                        "diameter": {"description": "size in cm.", "type": "integer",},
                        "plantDate": {
                            "type": "string",
                            "description": "the date the tree was planted.",
                        },
                    },
                },
            }
        ],
    }
