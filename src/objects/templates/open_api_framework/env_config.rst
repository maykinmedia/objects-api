{% extends "open_api_framework/env_config.rst" %}

{% block intro %}
Open Objecten can be run as a Docker container or a VPS / dedicated server.
It relies on other services, such as database and cache backends, which can be configured through environment variables.
{% endblock %}

{% block extra %}

Initial superuser creation (Docker only)
----------------------------------------

A clean installation of Open Objecten comes without pre-installed or pre-configured admin
user by default.

Users can opt-in to provision an initial superuser via environment
variables. The user will only be created if it doesn't exist yet.

* ``OBJECTS_SUPERUSER_USERNAME``: specify the username of the superuser to create. Setting
  this to a non-empty value will enable the creation of the superuser. Default empty.
* ``OBJECTS_SUPERUSER_EMAIL``: specify the e-mail address to configure for the superuser.
  Defaults to `admin@admin.org`. Only has an effect if ``OBJECTS_SUPERUSER_USERNAME`` is set.
* ``OBJECTS_SUPERUSER_PASSWORD``: specify the password for the superuser. Default empty,
  which means the superuser will be created _without_ password. Only has an effect
  if ``OBJECTS_SUPERUSER_USERNAME`` is set.

Initial configuration
---------------------

Open objecten supports the `setup_configuration` management command,
which allows configuration via environment variables.
All these environment variables are described at :ref:`command line <installation_config_cli>`.

{% endblock %}
