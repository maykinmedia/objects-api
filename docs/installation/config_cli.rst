.. _installation_config_cli:


===================
Configuration (CLI)
===================

After deploying Objecttypes API and Objects API, they need to be configured to be fully functional. The
command line tool `setup_configuration`_ assist with this configuration:

You can get the full command documentation with:

.. code-block:: bash

    src/manage.py setup_configuration --help

.. warning:: This command is declarative - if configuration is manually changed after
   running the command and you then run the exact same command again, the manual
   changes will be reverted.

.. _`setup_configuration`: https://github.com/maykinmedia/django-setup-configuration/

Preparation
===========

The command executes the list of pluggable configuration steps, and each step
requires specific configuration information, that should be prepared.
Here is the description of all available configuration steps and the configuration
format, use by each step.

Objects API
===========

Objecttypes configuration
-------------------------

To configure objecttypes the following configuration could be used:

.. code-block:: yaml
   ...
   zgw_consumers_config_enable: true
   zgw_consumers:
   services:
     - identifier: objecttypen-foo
       label: Objecttypen API Foo
       api_root: http://objecttypen.foo/api/v1/
       api_type: orc
       auth_type: api_key
       header_key: Authorization
       header_value: Token ba9d233e95e04c4a8a661a27daffe7c9bd019067

     - identifier: objecttypen-bar
       label: Objecttypen API Bar
       api_root: http://objecttypen.bar/api/v1/
       api_type: orc
       auth_type: api_key
       header_key: Authorization
       header_value: Token b9f100590925b529664ed9d370f5f8da124b2c20

   objecttypes_config_enable: true
   objecttypes:
     items:
       - uuid: b427ef84-189d-43aa-9efd-7bb2c459e281
         name: Object Type 1
         service_identifier: objecttypen-foo

       - uuid: b0e8553f-8b1a-4d55-ab90-6d02f1bcf2c2
         name: Object Type 2
         service_identifier: objecttypen-bar
   ...
.. note:: The ``uuid`` field will be used to lookup existing ``ObjectType``'s.

Objecttypes require a corresponding ``Service`` to work correctly. Creating
these ``Service``'s can be done by defining these in the same yaml file. ``Service``
instances will be created before the ``ObjectType``'s are created.

Objecttypes connection configuration
------------------------------------

In order to be able to retrieve objecttypes, a corresponding ``Service`` should be
created. An example of a configuration could be seen below:

.. code-block:: yaml
   ...

    zgw_consumers_config_enable: true
    zgw_consumers:
      services:
      - identifier: objecttypes-api-1
        label: Objecttypes API 1
        api_root: http://objecttypes-1.local/api/v1/
        api_connection_check_path: objecttypes
        api_type: orc
        auth_type: api_key
        header_key: Authorization
        header_value: Token ba9d233e95e04c4a8a661a27daffe7c9bd019067
      - identifier: objecttypes-api-2
        label: Objecttypes API 2
        api_root: http://objecttypes-2.local/api/v1/
        api_connection_check_path: objecttypes
        api_type: orc
        auth_type: api_key
        header_key: Authorization
        header_value: Token b9f100590925b529664ed9d370f5f8da124b2c20
   ....

Tokens configuration
--------------------

Mozilla-django-oidc-db
----------------------

Sites configuration
-------------------

Notifications configuration
-------------------------

To configure sending notifications for the application ensure there is a ``services``
item present that matches the ``notifications_api_service_identifier`` in the
``notifications_config`` namespace:

.. code-block:: yaml
   ...

    zgw_consumers_config_enable: true
    zgw_consumers:
      services:
      - identifier: notifications-api
        label: Notificaties API
        api_root: http://notificaties.local/api/v1/
        api_connection_check_path: notificaties
        api_type: nrc
        auth_type: api_key

    notifications_config_enable: true
    notifications_config:
      notifications_api_service_identifier: notifications-api
      notification_delivery_max_retries: 1
      notification_delivery_retry_backoff: 2
      notification_delivery_retry_backoff_max: 3
   ....


Execution
=========


With the full command invocation, everything is configured at once and immediately
tested.

.. code-block:: bash

    src/manage.py setup_configuration --yaml-file /path/to/config.yaml
