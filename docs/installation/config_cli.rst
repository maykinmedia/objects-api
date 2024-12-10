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

Objecttypes configuration
-------------------------

Create or update a (single) YAML configuration file with your settings:

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
     - identifier: objecttypen-bar
       label: Objecttypen API Bar
       api_root: http://objecttypen.bar/api/v1/
       api_type: orc
       auth_type: api_key

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


Execution
=========


With the full command invocation, everything is configured at once and immediately
tested.

.. code-block:: bash

    src/manage.py setup_configuration --yaml-file /path/to/config.yaml
