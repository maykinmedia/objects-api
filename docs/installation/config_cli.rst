.. _installation_config_cli:


===================
Configuration (CLI)
===================

.. setup-config-usage::
  :show_command_usage: true
  :show_steps: false
  :show_steps_toc: false
  :show_steps_autodoc: false

Objects API
===========

.. setup-config-usage::
  :show_command_usage: false

Objecttypes API
===============

.. FIXME these can currently only be included manually, because these docs are built in
.. the objects API repo

.. autoclass:: django_setup_configuration.contrib.sites.steps.SitesConfigurationStep
  :noindex:
.. setup-config-example:: django_setup_configuration.contrib.sites.steps.SitesConfigurationStep

.. autoclass:: mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep
  :noindex:
.. setup-config-example:: mozilla_django_oidc_db.setup_configuration.steps.AdminOIDCConfigurationStep


**objecttypes.setup_configuration.steps.token_auth.TokenAuthConfigurationStep**
-------------------------------------------------------------------------------

Configure tokens with permissions for other applications to access Objectstypes API

.. code-block:: yaml

  tokenauth_config_enable: true
  tokenauth:

    # REQUIRED: true
    items:
      -

        # DESCRIPTION: A human-friendly label to refer to this token
        # REQUIRED: true
        identifier: objects-api

        # REQUIRED: true
        token: modify-this

        # DESCRIPTION: Name of the person in the organization who can access the API
        # REQUIRED: true
        contact_person: example_string

        # DESCRIPTION: Email of the person, who can access the API
        # REQUIRED: true
        email: example_string

        # DESCRIPTION: Organization which has access to the API
        # DEFAULT VALUE: ""
        # REQUIRED: false
        organization: example_string

        # DESCRIPTION: Application which has access to the API
        # DEFAULT VALUE: ""
        # REQUIRED: false
        application: example_string

        # DESCRIPTION: Administration which has access to the API
        # DEFAULT VALUE: ""
        # REQUIRED: false
        administration: example_string
