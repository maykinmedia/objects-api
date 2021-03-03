.. _api_usage:

=========
API Usage
=========

If you don't know where to start with Objects and Objecttypes API here you can
find the examples of their usage.
Before going straight to the examples make sure that authorization is set up in APIs
and you know API tokens.

Objecttype API
==============

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
---------------------

Now we need to create an object type which will include this JSON schema, which consist of
creation metadata of the object type and adding actual data with JSON schema. This separation
exists because Objecttypes API supports versioning of object types. If you want to change JSON
schema in the objecttype its new version will be created. Therefore you don't need to worry
that a new version of the Object type schema would not match the exising objects in Objects API.

So let's create metadata:

.. code-block:: http

    POST /api/v1/objecttypes HTTP/1.1

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

    HTTP/1.1 201 Created

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

    POST /api/v1/objecttypes/<object-type-uuid>/versions HTTP/1.1

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
------------------------------

Let's publish our object type version. In Objecttypes API you can do it with regular
PATCH request:

.. code-block:: http

    PATCH /api/v1/objecttypes/<object-type-uuid>/versions/1 HTTP/1.1

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

    PATCH /api/v1/objecttypes/<object-type-uuid>/versions/1 HTTP/1.1

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

Once the object type is created it can always be retrieved by its url:

.. code-block:: http

    GET /api/v1/objecttypes/<object-type-uuid> HTTP/1.1

    HTTP/1.1 200 OK

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


Objects API
===========

Now we have an object type containing JSON schema for tree objects and we are ready to
create objects. Before going further please, make sure that you configured authorizations
in the admin:

* Objects API can access objecttypes API
* token which you use have permissions for a new object type.

Create an object
----------------

First of all let's construct tree data that match a related JSON schema in Objecttypes API:

.. code-block:: json

    {
        "boomgroep": "Solitaire boom",
        "boomhoogteactueel": 3,
        "leeftijd": 100,
        "meerstammig": false
    }

https://jsonschema.dev can be used to validate JSON data against JSON schema.

Using the url of the created object type we can create a tree object. If we have
GEO coordinates for our object we can also include them into the request body.

.. code-block:: http

    POST /api/v1/objects HTTP/1.1

    {
        "type": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "record": {
            "typeVersion": 1,
            "startAt": "2021-01-01",
            "data": {
                "boomgroep": "Solitaire boom",
                "boomhoogteactueel": 3,
                "leeftijd": 100,
                "meerstammig": false
            },
            "geometry": {
                "type": "Point",
                "coordinates": [4.908722727852763, 52.36991749536178]
            }
        }
    }

An object type version is defined in ``typeVersion`` attribute. This means that we can create
objects that match any version of the particular object type. The response contains the
url of the object:

.. code-block:: http

    HTTP/1.1 201 Created

    {
        "url": "http://<object-host>/api/v1/objects/<object-uuid>",
        "type": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "record": {
            "index": 1,
            "typeVersion": 1,
            "data": {
                "leeftijd": 100,
                "boomgroep": "Solitaire boom",
                "meerstammig": false,
                "boomhoogteactueel": 3
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.908722727852763,
                    52.36991749536178
                ]
            },
            "startAt": "2021-01-01",
            "endAt": null,
            "registrationAt": "2021-03-03",
            "correctionFor": null,
            "correctedBy": null
        }
    }

When an object is being created or updated its data is always validated against
JSON schema in the related object type. If the data doesn't match the response will
contain 400 error.

For example, let's try to create the following object:

.. code-block:: http

    POST /api/v1/objects HTTP/1.1

    {
        "type": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "record": {
            "typeVersion": 1,
            "startAt": "2021-03-03",
            "data": {
                "boomgroep": "Solitaire boom",
                "boomhoogteactueel": 2.5,
                "leeftijd": 100,
            }
        }
    }

In the JSON schema ``boomhoogteactueel`` is integer, so the response will look like this:

.. code-block:: http

    HTTP/1.1 400 Bad Request

    {
        "non_field_errors": [
            "2.5 is not of type 'integer'"
        ]
    }


Retrieve an object
------------------

Once the object is created it can always be retrieved by its url:

.. code-block:: http

    GET /api/v1/objects/<object-uuid> HTTP/1.1

    HTTP/1.1 200 OK

    {
        "url": "http://<object-host>/api/v1/objects/<object-uuid>",
        "type": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
        "record": {
            "index": 1,
            "typeVersion": 1,
            "data": {
                "leeftijd": 100,
                "boomgroep": "Solitaire boom",
                "meerstammig": false,
                "boomhoogteactueel": 3
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.908722727852763,
                    52.36991749536178
                ]
            },
            "startAt": "2021-01-01",
            "endAt": null,
            "registrationAt": "2021-03-03",
            "correctionFor": null,
            "correctedBy": null
        }
    }

Retrieve objects of certain object type
---------------------------------------

Objects API supports different searches through the objects.
You can filter objects on:

* object type
* data attributes (display all trees higher than 2 meters)
* GEO coordinates (display all trees in one neighbourhood)

To list on a particular object type you can use ``type`` query parameter:

.. code-block:: http

    GET /api/v1/objects?type=http://<object-type-host>/api/v1/objecttypes/<object-type-uuid> HTTP/1.1

    HTTP/1.1 200 OK

    [
        {
            "url": "http://<object-host>/api/v1/objects/<object-uuid>",
            "type": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
            "record": {
                "index": 1,
                "typeVersion": 1,
                "data": {
                    "leeftijd": 100,
                    "boomgroep": "Solitaire boom",
                    "meerstammig": false,
                    "boomhoogteactueel": 3
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.908722727852763,
                        52.36991749536178
                    ]
                },
                "startAt": "2021-01-01",
                "endAt": null,
                "registrationAt": "2021-03-03",
                "correctionFor": null,
                "correctedBy": null
            }
        }
    ]

Retrieve a history of an object
-------------------------------
Objects API supports versioning, i.e. when object is updated its previous states
which are called here as object records can also be accessed.

.. code-block:: http

    GET /api/v1/objects/<object-uuid>/history HTTP/1.1

    HTTP/1.1 200 OK

    [
        {
            "index": 1,
            "typeVersion": 1,
            "data": {
                "leeftijd": 100,
                "boomgroep": "Solitaire boom",
                "meerstammig": false,
                "boomhoogteactueel": 3
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    4.908722727852763,
                    52.36991749536178
                ]
            },
            "startAt": "2021-01-01",
            "endAt": null,
            "registrationAt": "2021-03-03",
            "correctionFor": null,
            "correctedBy": null
        }
    ]

For now we have only one record, but every time the object is changed the new record will
be created.

Retrieve an object version for a particular date
------------------------------------------------

Since there could be a difference between the real date of
the object change and its registration in the system the Objects API support both
formal and material history. The formal history describes the history as it should
be (stored in the ``startAt`` and ``endAt`` attributes). The material history describes the
history as it was administratively processed (stored in the ``registeredAt``
attribute).

The query parameters ``date`` (formal history) and ``registrationDate`` (material history)
allow for querying the RECORDS as seen from both perspectives, and can yield different results.

For example you want to display all the object with there states actual for 2021-02-02.
First, let's do it from formal history perspective:

.. code-block:: http

    GET /api/v1/objects?date=2021-02-02 HTTP/1.1

    HTTP/1.1 200 OK

    [
        {
            "url": "http://<object-host>/api/v1/objects/<object-uuid>",
            "type": "http://<object-type-host>/api/v1/objecttypes/<object-type-uuid>",
            "record": {
                "index": 1,
                "typeVersion": 1,
                "data": {
                    "leeftijd": 100,
                    "boomgroep": "Solitaire boom",
                    "meerstammig": false,
                    "boomhoogteactueel": 3
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        4.908722727852763,
                        52.36991749536178
                    ]
                },
                "startAt": "2021-01-01",
                "endAt": null,
                "registrationAt": "2021-03-03",
                "correctionFor": null,
                "correctedBy": null
            }
        }
    ]

We received our tree object in the response, because formally it started existing at 2021-01-01
(``startAt``) and never ceased (``endAt`` is empty).

Now let's do the same but from material history perspective:

.. code-block:: http

    GET /api/v1/objects?registrationDate=2021-02-02 HTTP/1.1

    HTTP/1.1 200 OK

    []

Our tree object was created at 2021-03-03 (``registrationAt``), so it hasn't existed at
2021-02-02 yet and Object API responses with empty list.
