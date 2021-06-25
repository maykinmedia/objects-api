Documentation
=============

The :ref:`Objects API` and the Objecttypes API are two components that complement
each other. The :ref:`Objecttypes API` holds the object definitions for objects that
can be stored in the Objects API. Together they provide a powerful way to
create and store any kind of object.

Designed in line with the `Common Ground`_ model, they can be used by other APIs that need
to store object specific data.

Both the Objects API and the Objecttypes API are and only use
:ref:`introduction_open-source`.

.. _`Common Ground`: https://commonground.nl/

Getting started
---------------

To get you started, you might find some of these links relevant:

* New to this project? Have a look at the :ref:`introduction_index`
* New to the API? Read up on the :ref:`api_index`.
* Want to get started now? Follow the :ref:`installation_quickstart`
* Want to know how the admin interface works? Go to the :ref:`admin_index`


.. _Objecttypes API:

Objecttypes API
---------------

Standardize various types of objects in an accessible way and without the need to create
a whole new API for each (simple) object.

This national level API is required for registering objects in local
:ref:`Objects APIs`. Organizations can also run the API locally, to use
both national and local definitions of objects.


.. _Objects API:
.. _Objects APIs:

Objects API
-----------

Easily store and expose various objects and make them
available in a standardized format. It can be used by any
organization to manage relevant objects. An organization can also choose to use it
to expose objects to the public as *Open Data*.

To define the format of objects, organizations can use
a national and/or local :ref:`Objecttypes API`.


.. toctree::
   :maxdepth: 2
   :hidden:

   introduction/index
   api/index
   admin/index
   installation/index
   examples/index
