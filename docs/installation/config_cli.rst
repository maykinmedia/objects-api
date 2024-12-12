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
      - identifier: objecttypes-api-2
        label: Objecttypes API 2
        api_root: http://objecttypes-2.local/api/v1/
        api_connection_check_path: objecttypes
        api_type: orc
        auth_type: api_key
   ....

Tokens configuration
-------------------

Notifications configuration
-------------------------

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
