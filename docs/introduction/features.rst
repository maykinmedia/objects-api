Features
========

Below is a list of the high level features of the APIs.

Objecttypes API
---------------

* **JSON-schema validation**

  When creating a new objecttype, the JSON-schema is validated. Only valid 
  JSON-schemas are allowed in the objecttype.

* **Versioning**

  Objecttypes are versioned. This means you can create an objecttype but it the
  objecttype evolves, you can create a new version.

* **Admin interface**

  You can create and inspect objecttypes via a user interface, meant for 
  administrators.

Objects API
-----------

* **Objecttype validation**

  When creating an object, the objecttype is inspected to see if all data is
  formatted according to the JSON-schema in the objecttype.

* **Formal and administrative history**

  The history of each object is recorded on two axes: The formal (formele) 
  history and the material (materiële) history.

* **Geographic search**

  Objects can be searched with GeoJSON using an arbitrary geographical point or
  polygon.

* **Arbitrary attribute filtering**

  Since the Objects API contains many different objects of different 
  objecttypes, the attributes are different for each objecttype. The Objects
  API supports filtering on any attribute.

* **Authorizations**

  With an API-token applications can get read or write access, per objecttype.
  These API-tokens can be configured in the admin interface.
