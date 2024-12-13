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
format, used by each step.

Objects API
===========

Sites configuration
-------------------

Create or update a (single) YAML configuration file with your settings:

.. code-block:: yaml
   ...
    sites_config_enable: true
    sites_config:
      items:
        - domain: example.com
          name: Example site

        - domain: test.example.com
          name: Test site
   ...

.. note:: The ``domain`` field will be used to lookup existing ``Site``'s.

Objecttypes connection configuration
-------------------------

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

TokenAuth configuration
-------------------------

Create or update a (single) YAML configuration file with your settings:

.. code-block:: yaml
    token_tokenauth_config_enable: true
    token_tokenauth:
      items:
        - identifier: token-1
          token: 18b2b74ef994314b84021d47b9422e82b685d82f
          contact_person: Person 1
          email: person-1@example.com
          organization: Organization XYZ
          application: Application XYZ
          administration: Administration XYZ
        
        - identifier: token-2
          token: e882642bd0ec2482adcdc97258c2e6f98cb06d85
          contact_person: Person 2
          email: person-2@example.com
   ...


Execution
=========


With the full command invocation, everything is configured at once.
Each configuration step is idempotent, so any manual changes made via the admin interface
will be updated if the command is run afterwards.

.. code-block:: bash

    python ./src/manage.py setup_configuration --yaml-file /path/to/config.yaml
