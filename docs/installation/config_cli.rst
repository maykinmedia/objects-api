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

Tokens configuration
-------------------

Notifications configuration
-------------------------

Mozilla-django-oidc-db
----------------------

Sites configuration
-------------------

Execution
=========


With the full command invocation, everything is configured at once and immediately
tested.

.. code-block:: bash

    src/manage.py setup_configuration --yaml-file /path/to/config.yaml
