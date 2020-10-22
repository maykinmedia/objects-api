Definitions
===========

Objecttype
----------

A definition, represented as a JSON-schema, together with metadata about the 
objecttype. Each *objecttype* represents a collection of *objects* of similar form 
and/or function.

Object
------

A self-contained entity of data with its own identity, structured according to
the JSON-schema of the *objecttype*.

*Example*

The *objecttype tree* has 2 attributes: `height` and `type`. A particular street 
has 3 trees, or rather, *3 objects of objecttype tree*, and they are: 1) 
`height`: 4.9m, `type`: oak, 2) `height`: 5.1m, `type`: oak, 3) `height`: 5.0m, 
`type`: pine tree.

Objecttypes API
---------------

An API to retrieve one or more *objecttypes*.

The Objecttypes API aims to standardize various types of objects, on a national
or just as easily on a local municipality level, and make them accessible as
resources for other applications.

Objects API
-----------

An API to retrieve, filter, search, write or update *objects*.

The Objects API aims to easily store and expose various objects according to 
the related **objecttype resource** in the *Objecttypes API*.
