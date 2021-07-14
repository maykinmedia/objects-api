Definitions
===========

Objecttype
----------

- A definition, represented as a JSON-schema, together with metadata about the objecttype. Each *objecttype* represents a collection of *objects* of similar form and/or function.

e.g. The *objecttype* tree has 2 attributes: ``height`` and ``type``. This will hold a definition for future objects.

Object
------

- A self-contained entity of data with its own identity, structured according to the JSON-schema of the *objecttype*.

e.g. A particular street
has 3 trees. That means there are 3 *objects* of *objecttype* ``tree``:

#. ``height``: 4.9m, ``type``: oak
#. ``height``: 5.1m, ``type``: oak
#. ``height``: 5.0m, ``type``: pine tree

Objecttypes API
---------------

- An API to retrieve (one or more) *objecttypes*.

Standardize various types of objects, on a national
or just as easily on a local municipality level, and make them accessible as
resources for other applications.

Objects API
-----------

- An API to retrieve, filter, search, write, update or delete *objects*.

Easily store and expose various objects according to
the related *objecttype* resource in the *Objecttypes API*.
