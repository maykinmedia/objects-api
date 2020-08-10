
Vision
======

It is almost impossible to know and to define each object in advance and create 
an appropriate API for it. This would cause significant slowdown of the 
implementation of the Common Ground principles and the IT-landscape would see
a huge amount of API's for each and every object type.

We are therefore introducing 2 complementing API's:

Objecttypes API
---------------

At a national level, there should be a registration for all kinds of object 
types. The object types hold the definition of an object and these definitions
can be obtainined via an API, the Objecttypes API.

The definition of an object can be proposed by domain experts and approved by 
the VNG to become part of the national Objecttypes API. An organization can 
also use its own Objecttypes API to hold definitions of locally defined objects.

Objects API
-----------

An organization can set up one or more Objects APIs. Each object in the Objects
API should adhere to a definition in the Objecttypes API.

Organizations can use one Objects API to store all objects, or set up multiple
Objects API to seperate between domains and/or open and internal data.

With the above setup, applications can now easily use objects that use the same 
definition in all organizations that rely on the same object type.
