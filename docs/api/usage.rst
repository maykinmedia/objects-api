.. _api_usage:

=========
API Usage
=========

If you don't know where to start with Objects and Objecttypes API here you can
find the examples of their usage.
Before going straight to the examples make sure that authorization is set up in APIs
and you know API tokens.

Objecttype API
=================

Let's start with creating an object type. For example, you want to store data
about trees in your town. First, you need to decide which attributes your data
will have and to design JSON schema for trees. You can take a look at provided
:ref:`examples_index`. Here is a JSON schema which we will use in the example:

.. code-block:: json

    {
      "$schema": "http://json-schema.org/draft-07/schema",
      "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
      "type": "object",
      "title": "Boom",
      "description": "Een houtachtig gewas (loofboom of conifeer) met een wortelgestel en een enkele, stevige, houtige stam, die zich boven de grond vertakt.",
      "properties": {
        "boomgroep": {
          "$id": "#/properties/boomgroep",
          "type": "string",
          "title": "Boomgroep",
          "description": "Aanduiding of de boom onderdeel is van een boomgroep.",
          "examples": [
            "Laanboom"
          ],
          "enum": [
            "Laanboom",
            "Boomweide",
            "Solitaire boom"
          ]
        },
        "boomhoogteactueel": {
          "$id": "#/properties/boomhoogteactueel",
          "type": "integer",
          "title": "BoomhoogteActueel",
          "description": "Hoogte van de boom in meters.\nEenheid: m"
        },
        "leeftijd": {
          "$id": "#/properties/leeftijd",
          "type": "integer",
          "title": "Leeftijd",
          "description": "Leeftijd van het beheerobject in jaren.\nEenheid: Aantal",
          "examples": []
        },
        "meerstammig": {
          "$id": "#/properties/meerstammig",
          "type": "boolean",
          "title": "Meerstammig",
          "description": "Aanduiding voor meerstammigheid bij een Boom"
        },
        "type": {
          "$id": "#/properties/type",
          "type": "string",
          "title": "Type",
          "description": "Typering van het beheerobject."
        }
      },
      "required": ["boomhoogteactueel", "leeftijd"]
    }


Create an object type
--------------------------

Now we need to create an object type which will include this JSON schema, which consist of
creation metadata of the object type and adding actual data with JSON schema. This separation
exists because Objecttypes API supports versioning of object types. If you want to change JSON
schema in the objecttype its new version will be created. Therefore you don't need to worry
that a new version of the Object type schema would not match the exising objects in Objects API.

So let's create metadata:

.. code-block:: http

    POST http://<object-type-host>/api/v1/objecttypes HTTP/1.1

    {
        "name": "boom",
        "namePlural": "bomen",
        "description": "Bomen in de publieke ruimte.",
        "dataClassification": "open",
        "maintainerOrganization": "Tree organization",
        "maintainerDepartment": "Tree API department",
        "contactPerson": "John Smith",
        "contactEmail": "john@lovestrees.nl",
        "source": "Tree navigator",
        "updateFrequency": "monthly",
        "providerOrganization": "Open data for trees",
        "documentationUrl": "http://tree-object-type.nl"
    }

The response contains the url of a freshly created object type with its unique identifier:

.. code-block:: http

    HTTP/1.1 201 OK

    {
        "url": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "name": "boom",
        "namePlural": "bomen",
        "description": "Bomen in de publieke ruimte.",
        "dataClassification": "open",
        "maintainerOrganization": "Tree organization",
        "maintainerDepartment": "Tree API department",
        "contactPerson": "John Smith",
        "contactEmail": "john@lovestrees.nl",
        "source": "Tree navigator",
        "updateFrequency": "monthly",
        "providerOrganization": "Open data for trees",
        "documentationUrl": "http://tree-object-type.nl",
        "labels": {},
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "versions": []
    }

Now we can add our JSON schema to the created object type as its version:

.. code-block:: http

    POST http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>/versions HTTP/1.1

    {
        "status": "draft",
        "jsonSchema": {
            "$schema": "http://json-schema.org/draft-07/schema",
            "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
            <...>
        }
    }

The response contains the url of the created version of the object type.

.. code-block:: http

    HTTP/1.1 201 OK

    {
        "url": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>/versions/1",
        "version": 1,
        "objectType": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "status": "draft",
        "jsonSchema": {
            "$schema": "http://json-schema.org/draft-07/schema",
            "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
            <...>
        },
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "publishedAt": null
    }

You can see that the version has 'draft' status, which means, that it can be updated.
Once the version's status is changed to 'published' you can't change it anymore.

Publish an object type version
-----------------------------------

Let's publish our object type version. In Objecttypes API you can do it with regular
PATCH request:

.. code-block:: http

    PATCH http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>/versions/1 HTTP/1.1

    {
        "status": "published"
    }

In response you can see that ``publishedAt`` attribute contains a current date now:

.. code-block:: http

    HTTP/1.1 200 OK

    {
        "url": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>/versions/1",
        "version": 1,
        "objectType": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "status": "published",
        "jsonSchema": {
            "$schema": "http://json-schema.org/draft-07/schema",
            "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
            <...>
        },
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "publishedAt": "2021-03-03"
    }


Now when you try to change this version 400 error will always appear.
For example:

.. code-block:: http

    PATCH http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>/versions/1 HTTP/1.1

    {
        "jsonSchema": {
        "$schema": "http://json-schema.org/draft-07/schema",
        "$id": "https://api.vng.nl/objecttypes/boom/schema.json",
        <...>
        "required": []
        }
    }

The response should be something like this:

.. code-block:: http

    HTTP/1.1 400 Bad Request

    {
        "non_field_errors": [
            "Only draft versions can be changed"
        ]
    }


Retrieve an objecttype
----------------------

Once the object type is created it can always be retrieved with its url:

.. code-block:: http

    GET http://<object-type-host>/api/v1/objecttypes/<object-type-uuid HTTP/1.1

    {
        "url": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "name": "boom",
        "namePlural": "bomen",
        "description": "Bomen in de publieke ruimte.",
        "dataClassification": "open",
        "maintainerOrganization": "Tree organization",
        "maintainerDepartment": "Tree API department",
        "contactPerson": "John Smith",
        "contactEmail": "john@lovestrees.nl",
        "source": "Tree navigator",
        "updateFrequency": "monthly",
        "providerOrganization": "Open data for trees",
        "documentationUrl": "http://tree-object-type.nl",
        "labels": {},
        "createdAt": "2021-03-03",
        "modifiedAt": "2021-03-03",
        "versions": [
            "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>/versions/1"
        ]
    }

You can see that ``versions`` attribute includes a list of urls to all the versions of this
object type.
