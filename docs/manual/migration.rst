.. _objecttype_migration:

ObjectTypes API migration
=========================

In version 4.0.0 the ObjectTypes API will be merged into the Objects API so that only one application is needed. This means that from version 4.0.0 only objecttypes that exist in the database are supported, and no external objecttypes can be used.

Importing objecttype data
-------------------------
Before updating to 4.0.0 all objecttypes from the ObjectTypes API instance need to be imported. This can be done with the ``import_objecttypes`` command that can be executed from the Objects container.
This command will fetch all objecttypes and their versions from an objecttype service based on its identifier/slug (which can be found in the admin interface under ``Configuration > Services``)
and update existing objecttypes or create new ones if they have not been added to the objecttypes API.

.. code-block:: bash

    src/manage.py import_objecttypes objecttypes-api

Please note that after the update the objecttypes API is still being used in Objects API version <4.0.0, the command only fetches and imports the data.
From 4.0.0 onwards it will use the imported objecttypes.
