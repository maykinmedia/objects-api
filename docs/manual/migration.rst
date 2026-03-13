.. _objecttype_migration:

ObjectTypes API migration
=========================

In version 4.0.0 the ObjectTypes API will be merged into the Objects API so that only one application is needed. This means that from version 4.0.0 only objecttypes that exist in the database are supported, and no external objecttypes can be used.

Importing objecttype data
-------------------------
Before updating to 4.0.0 all objecttypes from the ObjectTypes API instance need to be imported. This can be done with the ``import_objecttypes`` command that can be executed from the Objects container.
This command will fetch all objecttypes and their versions from an objecttype service based on its identifier/slug (which can be found in the admin interface under ``Configuration > Services``)
and update existing objecttypes or create new ones if they have not been added to the objecttypes API.

.. note::

    The minimum version of the Objecttypes API application required for this command is
    3.4.0

.. note::

    Objecttypen that exist in the objects API but have been removed from their objecttypen API should be removed since they cannot be imported.

.. code-block:: bash

    src/manage.py import_objecttypes objecttypes-api

Please note that after the update the objecttypes API is still being used in Objects API version <4.0.0, the command only fetches and imports the data.
From 4.0.0 onwards it will use the imported objecttypes (and the related objecttypes API could be turned off).


With ``check_for_external_objecttypes`` you can check if there are any remaining external objecttypes.

.. code-block:: bash

    src/manage.py check_for_external_objecttypes

Version flow
------------

Objects API versions below 3.6.0 first need be upgraded to 3.6.0 After 3.6.0 the instance can be upgraded to 4.0.0.
If there are remaining external objecttypes the container will fail and you will need to roll back to 3.6.0.

If it is on ``latest`` it should ideally go to 3.6.0 before upgrading to 4.0.0. If the latest tag is pulled and the container is updated,
it will not fail for remaining external objecttypes. This can be fixed by running ``import_objecttypes`` in 4.0.0 for each objecttype service.


Setup configuration
-------------------

Because of the migration the setup configuration models have also changed. Please make sure to update the config before upgrading to 4.0.0

Objecttypes
^^^^^^^^^^^

- removed service_identifier

TokenAuth
^^^^^^^^^

- removed use_fields
- removed fields
