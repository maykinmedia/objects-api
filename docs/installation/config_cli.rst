.. _installation_config_cli:


===================
Configuration (CLI)
===================

After deploying Objecttypes API and Objects API, they need to be configured to be fully functional. The
command line tool `setup_configuration`_ assist with this configuration:

* It uses environment variables for all configuration choices, therefore you can integrate this with your
  infrastructure tooling such as init containers and/or Kubernetes Jobs.
* The command can self-test the configuration to detect problems early on

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
required specific environment variables, that should be prepared.
Here is the description of all available configuration steps and the environment variables,
use by each step for both APIs.


Objects API
===========

Sites configuration
-------------------

Configure the domain where Objects API is hosted

* ``SITES_CONFIG_ENABLE``: enable Site configuration. Defaults to ``False``.
* ``OBJECTS_DOMAIN``:  a ``[host]:[port]`` or ``[host]`` value. Required.
* ``OBJECTS_ORGANIZATION``: name of Objects API organization. Required.

Objecttypes configuration
-------------------------

Objects API uses Objecttypes API to validate data against JSON schemas, therefore
it should be able to request Objecttypes API.

* ``OBJECTS_OBJECTTYPES_CONFIG_ENABLE``: enable Objecttypes configuration. Defaults
  to ``False``.
* ``OBJECTTYPES_API_ROOT``: full URL to the Objecttypes API root, for example
  ``https://objecttypes.gemeente.local/api/v1/``. Required.
* ``OBJECTTYPES_API_OAS``: full URL to the Objecttypes OpenAPI specification.
* ``OBJECTS_OBJECTTYPES_TOKEN``: authorization token. Required.
* ``OBJECTS_OBJECTTYPES_PERSON``: Objects API contact person. Required.
* ``OBJECTS_OBJECTTYPES_EMAIL``: Objects API contact email. Required.

Demo user configuration
-----------------------

Demo user can be created to check if Objects API work. It has superuser permissions,
so its creation is not recommended on production environment.

* ``DEMO_CONFIG_ENABLE``: enable demo user configuration. Defaults to ``False``.
* ``DEMO_PERSON``: demo user contact person. Required.
* ``DEMO_EMAIL``: demo user email. Required.
* ``DEMO_TOKEN``: demo token. Required.


Objecttypes API
===============

ObjectTypes API has similar configuration steps as the Objects API.

Sites configuration
-------------------

Configure the domain where Objects API is hosted

* ``SITES_CONFIG_ENABLE``: enable Site configuration. Defaults to ``True``.
* ``OBJECTTYPES_DOMAIN``:  a ``[host]:[port]`` or ``[host]`` value. Required.
* ``OBJECTTYPES_ORGANIZATION``: name of Objecttypes API organization. Required.

Objects configuration
---------------------

Objects API uses Objecttypes API to validate data against JSON schemas, therefore
it should be able to request Objecttypes API.

* ``OBJECTS_OBJECTTYPES_CONFIG_ENABLE``: enable Objecttypes configuration. Defaults
  to ``True``.
* ``OBJECTTYPES_API_ROOT``: full URL to the Objecttypes API root, for example
  ``https://objecttypes.gemeente.local/api/v1/``. Required.
* ``OBJECTTYPES_API_OAS``: full URL to the Objecttypes OpenAPI specification.
* ``OBJECTS_OBJECTTYPES_TOKEN``: authorization token. Required.

Demo user configuration
-----------------------

The similar configuration as in Objects API.

* ``DEMO_CONFIG_ENABLE``: enable demo user configuration. Defaults to the value of the ``DEBUG`` setting.
* ``DEMO_PERSON``: demo user contact person. Required.
* ``DEMO_EMAIL``: demo user email. Required.
* ``DEMO_TOKEN``: demo token. Required.


Execution
=========


With the full command invocation, everything is configured at once and immediately
tested.

.. code-block:: bash

    src/manage.py setup_configuration


You can skip the self-tests by using the ``--no-selftest`` flag.

.. code-block:: bash

    src/manage.py setup_configuration --no-self-test


``setup_configuration`` command checks if the configuration already exists before changing it.
If you want to change some of the values of the existing configuration you can use ``--overwrite`` flag.

.. code-block:: bash

    src/manage.py setup_configuration --overwrite
