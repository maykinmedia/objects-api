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

Sites configuration
-------------------

Create or update a (single) YAML configuration file with your settings:

.. code-block:: yaml
   ...
    sites_config_enable: true
    sites:
      items:
        - domain: example.com
          name: Example site

        - domain: test.example.com
          name: Test site
   ...

.. note:: The ``domain`` field will be used to lookup existing ``Site``'s.

Objecttypes connection configuration
-------------------------

Create or update a (single) YAML configuration file with your settings:

.. code-block:: yaml
   objecttypes_connection_config_enable: true
   objecttypes_connection:
     identifier: objecttypen
     label: ObjectTypen API
     api_root: http://objecttypen.nl/api/v1/
     api_connection_check_path: objecttypes
     api_type: orc
     auth_type: api_key
     header_key: Authorization
     header_value: Token foo
   ...


Execution
=========


With the full command invocation, everything is configured at once and immediately
tested.

.. code-block:: bash

    src/manage.py setup_configuration --yaml-file /path/to/config.yaml
