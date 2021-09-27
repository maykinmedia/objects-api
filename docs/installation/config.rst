.. _installation_environment_config:

===================================
Environment configuration reference
===================================

The Objects and Objecttypes APIs can be run both as a Docker container or a VPS / dedicated server. It relies on other services, such as
database and cache backends, which can be configured through environment
variables.

Available environment variables
===============================

Required settings
-----------------

* ``DJANGO_SETTINGS_MODULE``: which environment settings to use. Available options:

  - ``objects.conf.docker`` or ``objecttypes.conf.docker``
  - ``objects.conf.dev`` or ``objecttypes.conf.dev``
  - ``objects.conf.ci`` or ``objecttypes.conf.ci``

* ``SECRET_KEY``: secret key that's used for certain cryptographic utilities. You
  should generate one via
  `miniwebtool <https://www.miniwebtool.com/django-secret-key-generator/>`_

* ``ALLOWED_HOSTS``: A comma separated (without spaces!) list of domains that
  serve the installation. Used to protect against ``Host`` header attacks.
  Defaults to ``*`` for the ``docker`` environment and defaults to
  ``127.0.0.1,localhost`` for the ``dev`` environment.

Database settings
-----------------

* ``DB_HOST``: Hostname of the PostgreSQL database. Defaults to ``db`` for the
  ``docker`` environment, otherwise defaults to ``localhost``.

* ``DB_USER``: Username of the database user. Defaults to ``objects`` or ``objecttypes``,

* ``DB_PASSWORD``: Password of the database user. Defaults to ``objects`` or ``objecttypes``,

* ``DB_NAME``: Name of the PostgreSQL database. Defaults to ``objects`` or ``objecttypes``,

* ``DB_PORT``: Port number of the database. Defaults to ``5432``.

Other settings
--------------

* ``ADMINS``: Comma seperated list (without spaces!) of e-mail addresses to
  sent an email in the case of any errors. Defaults to an empty list.

* ``SITE_ID``: The database ID of the site object. Defaults to ``1``.

* ``DEBUG``: Used for more traceback information on development environment.
  Various other security settings are derived from this setting! Defaults to
  ``True`` for the ``dev`` environment, otherwise defaults to ``False``.

* ``IS_HTTPS``: Used to construct absolute URLs and controls a variety of
  security settings. Defaults to the inverse of ``DEBUG``.

* ``SUBPATH``: If hosted on a subpath, provide the value here. If you provide
  ``/gateway``, the component assumes its running at the base URL:
  ``https://somedomain/gateway/``. Defaults to an empty string.

* ``SENTRY_DSN``: URL of the sentry project to send error reports to. Defaults
  to an empty string (ie. no monitoring).

* ``NOTIFICATIONS_DISABLED``: indicates whether or not notifications should be
  sent to the Notificaties API for operations on the Object endpoint.
  Defaults to ``True`` for the ``dev`` environment, otherwise defaults to ``False``.

* ``TWO_FACTOR_FORCE_OTP_ADMIN``: Enforce 2 Factor Authentication in the admin or not.
  Default ``True``. You'll probably want to disable this when using OIDC.

* ``TWO_FACTOR_PATCH_ADMIN``: Whether to use the 2 Factor Authentication login flow for
  the admin or not. Default ``True``. You'll probably want to disable this when using OIDC.

* ``SUPERUSER_NAME``: the username of the superuser account that is created automatically
  after running migrations (if not specified, no superuser account is created)

* ``SUPERUSER_PASSWORD``: the password of the superuser account that is created automatically
  after running migrations (if not specified, no superuser account is created)

Specifying the environment variables
=====================================

There are two strategies to specify the environment variables:

* provide them in a ``.env`` file
* start the component processes (with uwsgi/gunicorn/celery) in a process
  manager that defines the environment variables

Providing a .env file
---------------------

This is the most simple setup and easiest to debug. The ``.env`` file must be
at the root of the project - i.e. on the same level as the ``src`` directory (
NOT *in* the ``src`` directory).

The syntax is key-value:

.. code::

   SOME_VAR=some_value
   OTHER_VAR="quoted_value"


Provide the envvars via the process manager
-------------------------------------------

If you use a process manager (such as supervisor/systemd), use their techniques
to define the envvars. The component will pick them up out of the box.
