==============
Change history
==============

3.1.2 (2025-07-22)
------------------

**Bugfixes/QOL**

* Fix Elastic APM not showing time spent in database when using connection pooling via envvars

**Maintenance**

* Add environment variable ``DB_DISABLE_SERVER_SIDE_CURSORS`` to disable server side cursors (see :ref:`installation_env_config` > Database for more information)
* Upgrade dependencies

  * ``django-privates`` to 3.1.1
  * ``commonground-api-common`` to 2.7.0
  * ``open-api-framework`` to 0.12.0

* Use DB connection pooling settings from ``open-api-framework``

.. warning::

  The connection pooling settings (via environment variables) apply to each uWSGI process and each replica, this means
  that when running with 2 replicas and 4 processes for example, there will effectively be 8
  connection pools with the above settings.

**Documentation**

* Fix incorrect default in docs for DB_CONN_MAX_AGE
* [:open-api-framework:`148`] Add prerequisites docs page
* [:open-api-framework:`118`] Remove outdated deployment tooling/docs

3.1.1 (2025-07-04)
------------------

**Bugfixes**

* [:objects-api:`619`] Fix unstructured logs still being emitted by the Celery container

**Project maintenance**

* [:objects-api:`587`] Add rule to disallow direct ``logging`` imports
* [:open-api-framework:`151`] Move ``ruff`` and ``bump-my-version`` configurations into ``pyproject.toml``
* [:open-api-framework:`149`] Add dark/light theme toggle to the admin interface
* [:open-api-framework:`139`] Integrate ``django-upgrade-check`` to ensure that all required versions are correctly handled during instance upgrades

* Upgrade dependencies:
  * django to 5.2.3
  * notifications-api-common to 0.7.3
  * commonground-api-common to 2.6.7
  * open-api-framework to 0.11.0
  * django-setup-configuration to 0.8.2
  * django-debug-toolbar to 5.2.0
  * zgw-consumers to 0.38.1
  * requests to 2.32.4
  * urllib3 to 2.5.0
  * vcrpy to 7.0.0

**Performance optimizations**

* [:objects-api:`615`] Improve admin ``listview`` search performance and usability


3.1.0 (2025-05-26)
------------------

**New features**

.. note::

  The logging format has been changed from unstructured to structured with `structlog <https://www.structlog.org/en/stable/>`_.
  For more information on the available log events and their context, see :ref:`manual_logging`.

* [:objects-api:`586`] Add log events for creation/updating of objects via the API

**Performance optimizations**

* [:objects-api:`538`] Apply caching to ``reverse`` calls in ``ObjectUrlField`` to avoid additional overhead
* [:objects-api:`538`] Avoid doing more queries than necessary for ``/objects`` endpoint

**Bugfixes and QOL**

* [:objects-api:`576`] Add missing ``type: object`` property to ``ObjectRecord`` in OAS
* Do not use ``save_outgoing_requests`` log handler if ``LOG_REQUESTS`` is set to false

**Project maintenance**

* [:objects-api:`562`] Fix security issues by upgrading packages in Dockerfile
* Upgrade dependencies:

  * ``tornado`` to 6.5.0 to fix security issues
  * ``josepy`` to 1.14.0
  * ``django-formtools`` to 2.5.1
  * ``open-api-framework`` to 0.10.1
  * ``commonground-api-common`` to 2.6.4

* [:open-api-framework:`140`] Upgrade python to 3.12
* Replace OAS workflows with single workflow
* [:open-api-framework:`133`] Replace black, isort and flake8 with ``ruff`` and update ``code-quality`` workflow
* Remove references to API test platform in README/documentation

3.0.4 (2025-05-13)
------------------

.. warning::

    This release upgrades Django to version 5.2.1, which requires PostgreSQL version 14 or higher.
    Attempting to deploy with PostgreSQL <14 will cause errors during deployment.

**Bugfixes and QOL**

* [:objects-api:`570`] Removed broken ObjectRecord geometry map widget.
* [:objects-api:`374`] Fixed empty token auth field when creating Permission for Token authorization.

**Project maintenance**

* Add additional performance tests for pagination
* Upgrade dependencies

  * django to 5.2.1
  * django-setup-configuration to 0.7.2
  * commonground-api-common to 2.6.2
  * httpcore to 1.0.9
  * h11 to 0.16.0

* Upgrade dev dependencies

  * django-webtest to 1.9.13

* Upgrade npm packages to fix vulnerabilities
* Fixed admin logout button
* [:objects-api:`550`] Implement cache for objecttypes
* [:objects-api:`550`] add OBJECTTYPE_VERSION_CACHE_TIMEOUT environment variable (see `documentation for environment variables for caching <https://objects-and-objecttypes-api.readthedocs.io/en/latest/installation/config.html#cache>`_)
* [:objects-api:`572`] Add db connection pooling environment variables (see `documentation for environment variables for database <https://objects-and-objecttypes-api.readthedocs.io/en/latest/installation/config.html#database>`_)

  * DB_POOL_ENABLED
  * DB_POOL_MIN_SIZE
  * DB_POOL_MAX_SIZE
  * DB_POOL_TIMEOUT
  * DB_POOL_MAX_WAITING
  * DB_POOL_MAX_LIFETIME
  * DB_POOL_MAX_IDLE
  * DB_POOL_RECONNECT_TIMEOUT
  * DB_POOL_NUM_WORKERS

* [:objects-api:`566`] Add DB_CONN_MAX_AGE environment variable (see `documentation for environment variables for database <https://objects-and-objecttypes-api.readthedocs.io/en/latest/installation/config.html#database>`_)

3.0.3 (2025-04-03)
------------------

**Project maintenance**

* [:open-api-framework:`59`] Deprecate django.contrib.sites and add ``SITE_DOMAIN`` environment variable
  as a replacement (see :ref:`installation_env_config` > Optional for more information)
* [:open-api-framework:`125`] Upgrade docker image to debian-bookworm
* [:open-api-framework:`117`] Confirm support for Postgres 17 and drop (verified) support for Postgres 12
* Confirm support for Postgis 3.2/3.5 and drop (verified) support for Postgis 2.5
* Upgrade nodejs version in Docker image to 20
* Upgrade dependencies

  * open-api-framework to 0.9.6
  * commonground-api-common to 2.5.5
  * notifications-api-common to 0.7.2

* Upgrade dev dependencies

  * black to 25.1.0
  * flake to 7.1.2
  * isort to 6.0.1

* [:open-api-framework:`116`] Fix codecov publish
* [:open-api-framework:`115`] Fix oas CI check

3.0.2 (2025-03-07)
------------------

**Bugfixes and QOL**

* [:objects-api:`538`] Optimize objects list performance
* [:objects-api:`523`] Added help text in Permission admin view to explain that authorization fields are
  reset when the Object type is changed

**Project maintenance**

* Upgrade dependencies:

  * [:objects-api:`541`] Upgrade kombu to 5.4.2, this should fix the issue that caused Celery workers
    to not be able to reestablish connections with Redis
  * Upgrade Django to 4.2.20
  * Upgrade jinja2 to 3.1.6 to fix security issue

* [:objects-api:`538`] Add performance test for objects API list
* [:objects-api:`538`] Add django-silk for performance profiling in development environment

3.0.1 (2025-03-04)
------------------

**Bugfixes and QOL**

* [:objects-api:`464`] improved performance of the permission page in the Admin :zap:
* [:open-api-framework:`79`] disabled admin nav sidebar

**Project maintenance**

* bumped python dependencies: open-api-framework to 0.9.3, commonground-api-common to 2.5.0, django to 4.2.19, cryptography to 44.0.1
* [:objects-api:`529`] added bump-my-version to dev dependencies
* [:open-api-framework:`44`] added workflow to CI to auto-update open-api-framework
* [:objects-api:`509`, :open-api-framework:`104`] updated quick-start workflow to test docker-compose.yml
* [:charts:`165`] remove unused celery worker command line args

**Documentation**

* [:objects-api:`521`] updated documentation for ``django-setup-configuration`` steps with YAML example directive

3.0.0 (2025-01-22)
------------------

**Breaking changes**

* removed objects-api V1 [#453]

2.5.0 (2025-01-09)
------------------

**Breaking changes**

* upgraded ``django-setup-configuration`` to ``0.5.0``

.. warning::

    Previous configuration files used for ``setup_configuration`` do not work.
    See :ref:`installation_config_cli` for the available settings that can now be configured through ``setup_configuration``.

* added support for configuring permissions through ``django-setup-configuration``
  version ``0.4.0`` [#497]
* added support for configuring token authorizations through ``django-setup-configuration``
  version ``0.4.0`` [#485]
* added support for configuring ``mozilla-django-oidc-db`` through ``django-setup-configuration``
  version ``0.4.0`` [#490]
* added support for configuring ``OBJECTTYPE``'s through ``django-setup-configuration``
  version ``0.4.0`` [#467]
* added support for configuring Notificatiescomponentconfiguratie through ``django-setup-configuration``
  version ``0.4.0`` [#484]

**New features**

* added the new ``data_attrs`` query parameter for the ``OBJECT``'s resource [#472]

.. warning::

    Usage of the `data_attr` query parameter is deprecated. Usage of the
    new `data_attrs` query parameter is recommended.

* updated OAF version to 0.9.1. This upgrade allows admin users managing their sessions through the admin.


**Bugfixes and QOL**

* fixed ``latest`` docker image tag not being pushed [open-api-framework/#92]
* fixed documentation building in CI [#501]
* included ``gettext`` in docker images [#495]
* updated zgw-consumers to 0.35.1 [open-api-framework/#66]

.. warning::

    Configuring external services is now done through the ``Service`` model. This
    replaces the ``APICredential`` model in the admin interface. A data migration
    was added to move to the `Service` model. It is advised to verify the ``Service``
    instances in the admin to check that the data migration was ran as expected.

* updated PATCH request behaviour for the ``data`` field [#466]
* fixed CSP errors [open-api-framework/#68]

**Project maintenance**

* implementend CI action to create a PR with latest OAF version [open-api-framework/#44]
* security updates [open-api-framework/#93]
* switched from ``pip-compile`` to ``uv`` [open-api-framework/#81]
* pinned ``publish`` workflow to ``v3.0.1`` [#504]
* implementend open-api-workflows [open-api-framework/#13]

**Documentation**

* added documentation for notification retry behavior [#403]
* added missing changelog entry [#455]

2.4.4 (2024-10-01)
------------------

**Bugfixes and QOL**

* fixed CSP errors on the OAS page (#458)
* fixed OIDC login by making SameSite setting lax (#458)
* fixed adding permissions in the Admin (#449)
* fixed ``NOTIFICATIONS_DISABLED`` setting (#452)

**Project maintenance**

* added CI action to check if OAF is up-to-date (#443)

2.4.3 (2024-09-18)
------------------

**New features**

* added an endpoint to retrieve a specific object version (#328)
* supported the `in` operator in `data_attrs` to match one element (#414)

**Bugfixes and QOL**

* hid previous records available on particular date even if they match search parameters (#324)
* fixed 2FA app title (#442)
* bumped setuptools and npm dependencies (#441)

**Project maintenance**

* disabled configuration steps by default (#446)
* increase default values for uwsgi processes and threads (#448)

.. warning::

    All configuration steps are now disabled by default. To enable them use the correspondent
    environment variables


2.4.2 (2024-08-26)
------------------

**New features**

* updated open-api-framework to 0.8.0, which includes adding CSRF, CSP and HSTS settings (#438).
  All new environment variables are added to the `documentation <https://objects-and-objecttypes-api.readthedocs.io/en/latest/installation/config.html>`_

.. warning::

    ``SECURE_HSTS_SECONDS`` has been added with a default of 31536000 seconds, ensure that
    before upgrading to this version of open-api-framework, your entire application is served
    over HTTPS, otherwise this setting can break parts of your application (see https://docs.djangoproject.com/en/4.2/ref/middleware/#http-strict-transport-security)

**Bugfixes and QOL**

* bumped python dependencies due to security issues: django, celery, certifi, maykin-2fa, mozilla-django-oidc-db,
  sentry-sdk, webob and others (#428)
* bumped ``zgw-consumers`` to 0.29.0 and updated a code for clients, because of zgw-consumers breaking change.
* paginated ``/api/v2/objects/{uuid}/history`` endpoint (#329)
* fixed ``"register_kanalen`` command (#426)
* fixed notification page link (open-zaak/open-notificaties#171)

** Documentation**

* updated the documentation of environment variables using open-api-framework (open-zaak/open-zaak#1649)


2.4.1 (2024-08-06)
------------------

**Bugfixes and QOL**

* added Celery healthcheck
* made user emails unique to prevent two users logging in with the same email,
  causing an error

**Project maintenance**

* added CI-job to check for unexpected changes in the OAS (#420)

.. warning::

    User email addresses will now be unique on a database level. The database
    migration will fail if there are already two or more users with the same
    email address. You must ensure this is not the case before upgrading.

2.4.0 (2024-07-05)
------------------

**New features**

* added superuser permissions to API (#369)
* added `setup_configuration` management command which can configure API with
  environment variables (#368)
* added `Record.data` as a search filter in the Admin (#381)
* displayed `Objecttype.uuid` in the Objecttype and Object admin pages (#315)

**Bugfixes and QOL**

* supported `correctionFor` = `null` in POST/PUT requests (#268)
* added tests for `additionalProperties` keyword in JSON schema (#330)
* fixed creating objects with empty data (#371)
* fixed displaying the Token admin page if Object Types API is unavailable (#373)
* fixed styling of OIDC login page (#392)
* fixed styling of the help text icon in the Admin (#421)
* updated demo data used in quick start process (#398, #400)

**Project maintenance**

* updated Python to 3.11 (#379)
* added `open-api-framework` dependency (#358)
* refactored settings using `open-api-framework` (#413)
* added logging of outgoind requests (#344)
* added Trivy into the CI as an docker image scaner (#402)
* added GitHub issue templates (#389)
* merged quick start and regular docker compose files into one (#408)
* changed caching backend from LocMem to Redis
* Elastic APM service name can now be configured with ``ELASTIC_APM_SERVICE_NAME`` envvar

**Documentation**

* added security policy (#390)
* updated Quick start documentation (#348)

.. warning::

    Because the caching backend was changed to Redis, existing deployments must add a Redis container or Redis instance
    (see ``Installation > Environment configuration reference`` in the documentation on how to configure) the connection with Redis

.. warning::

    The service name for Elastic APM is now configurable via the ``ELASTIC_APM_SERVICE_NAME`` environment variable.
    The default value changed from ``Objects API`` to ``objects - <ENVIRONMENT>``


2.3.2 (2024-05-03)
------------------

Bugfix release

This release addresses a security weakness.

* [GHSA-3wcp-29hm-g82c] replaced PK for Token model.


2.3.1 (2024-03-22)
------------------

**Bugfixes and QOL**

* fixed celery docker container (#376)
* configured caches with redis (#377)
* added flower to monitor celery tasks (#378)

.. note::

    Flower is added to the docker, so now flower container could be deployed for monitoring
    purposes.


2.3.0 (2024-03-15)
------------------

* Updated to Django 4.2.

.. warning::

    Celery (and thus Redis) is now a required dependency.

    Two-factor authentication is enabled by default. The ``DISABLE_2FA`` environment variable
    can be used to disable it if needed.

2.2.1 (2024-03-02)
------------------

**Bugfixes and QOL**

* fixes OIDC config page by adding ``django_jsonform`` to ``INSTALLED_APPS`` (#350)
* added ``USE_X_FORWARDED_HOST`` environment variable (#353)
* added email environment variables (#366)


2.2.0 (2024-01-30)
------------------

**Component changes**

* **Bugfixes and QOL**

* fixed Permission form in the Admin (#309)
* added ``ENVIRONMENT`` environment variable (#310)
* updated python from 3.7 to 3.10 (#357)
* bumped Django to 3.2 (#357)
* bumped python libraries including mozilla-django-oidc, mozilla-django-oidc-db, zgw-consumers, uwsgi (#357, #338)
* removed hijack library (#357)
* updated base for docker image from Debian 10 to Debian 12 (#357)

**API 2.2.0 changes**

* **New features**

  * added `typeVersion` query parameter (#306)
  * supported JSON merge when doing a partial update on ``data`` attribute (#351)

* **Bugfixes**

  * added `typeVersion` query parameter (#306)
  * fixed date-time parsing in API filtering (#308)

.. warning::

   Change in deployment is required. `/media/` volume should be configured to share OAS files.

   Explanation:

   The new version of ``zgw_consumers`` library adds ``oas_file`` filed to ``Service`` model.
   This field saves OAS file into ``MEDIA_ROOT`` folder.
   The deployment now should have a volume for it.
   Please look at the example in ``docker-compose.yml``

2.1.1 (2022-06-24)
------------------

* **Bugfixes and QOL**

  * fixed updating objects with earlier `startAt` attribute (#282)
  * removed boostrap from the landing page (#294)
  * bumped to newer versions of pyjwt (#299)
  * fixed Elastic APM configuration (#289)


2.1.0 (2022-05-17)
------------------

**Component changes**

* **Bugfixes and QOL**

  * managed 2FA authentication using environment variables (#250)
  * integrated with OpenID Connect (#246)
  * create initial superuser with environment variables (#254)
  * removed non-actual results when filtering on `data_attr` query param (#260)
  * supported objecttypes with json schemas without properties in the Objects Admin (#273)
  * bumped to newer versions of mozilla-django-oidc-db (#264), django, lxml, babel, waitress(#293), pillow (#285) and npm packages (#279)
  * remove swagger2openapi from dependencies (#292)

* **Deployment tooling / infrastructure**

  * use ansible collections from Ansible Galaxy (#241)

**API 1.3.0 changes**

* **New features**

  * supported numeric values for `icontains` query param (#262)
  * supported validation on `hasGeometry` field in the Objecttypes API (#263)

**API 2.1.0 changes**

* **New features**

  * supported numeric values for `icontains` query param (#262)
  * supported validation on `hasGeometry` field in the Objecttypes API (#263)
  * supported `ordering` query param which allows to sort the results (#274)


2.0.0 (2021-09-22)
------------------

**Component changes**

* Supports API 2.0.0 and API 1.2.0

**API 1.2.0 changes**

* **New features**

  * supported having several API versions at the same time (#195)
  * enabled selecting set of fields for every object type version which are allowed to display in the API (#79)
  * sent notifications when the objects are changed in the API using Notificaties API. Sending notifications is an optional feature that can be disabled (#221, #237)
  * added an endpoint to show which API permissions the client has (#81)
  * made `geometry` field non-required for the `search` endpoint (#236)
  * supported dates in the `data_attrs=` query param (#214)
  * supported `icontains` operator in the `data_attrs=` query param, which allows case-insensitive search on the part of the string (#235)
  * added two-factor authentication for the Objects Admin (#232)

* **Bugfixes and QOL**

  * bumped to newer versions of django, django-debug-toolbar, urllib3, sqlparse (#225, #243)
  * added superuser for quick-start (#203)
  * tested the performance of the API per version (#219)

* **Documentation**

  * marked read-only fields as non-required in OAS (#210)
  * described how to configure authorization with the set of allowed fields in the admin (#79)
  * documented how to configure notifications (#245)

**API 2.0.0 changes**

* **Breaking features**

  * paginated API responses (#148)

* **New features**

  * supported `data_icontains` query param which requires Postgres 12+ (#235)

* **Deployment tooling / infrastructure**

  * updated Postgres version in the Objects API Helm chart (#242)


1.1.1 (2021-06-22)
------------------

**Bugfixes and QOL**

* Fixed OAS generation: remove unrelated error response bodies and headers, swap the notion of material and formal history (#197, #201)
* Tested the implementation of the material and formal history (#168)

**Documentation**

* Documented how to use the Objecttypes admin and the Objects admin (#60)


1.1.0 (2021-04-21)
------------------

**New features**

* Decoupled authentication tokens from users in the admin (#115)
* Added additional fields for tokens to store extra information (#155)
* Adhered the Objecttypes API to API principles API-09, API-18, API-19, API-51 defined in API Design Rules of Nederlandse API Strategie (#46, #174)
* Supported `fields=` query param and display only selected fields in the API response (#174)
* Added length validation fo url fields (#154)
* Improved the Admin UI:

  * Include `uuid` field to the "object" page (#156)
  * Make `object_type` field immutable (#150)
  * Add filtering on `object_type` to the "object" page (#157)

**Bugfixes and QOL**

* Improved performance with database query optimization (#136) :zap:
* Bumped to newer versions of Django, Jinja2, Pillow, PyYAML, pip-tools including security fixes (#183, #182, #184, #176, #193)
* Fixed a crash when creating an object without a version in the admin (#146)

**Deployment tooling / infrastructure**

* Added Helm chart to deploy the Objects API on Kubernetes (#180)
* Added Ansible configuration to deploy the Objects API on single server (#59)

**Documentation**

* Added a tutorial how to use the Objects API and the Objecttypes API with examples (#61)
* Documented how to configure authentication and authorization for the Objects API and the Objecttypes API (#179)
* Documented deployment of the Objects API and the Objecttypes API on single server and Kubernetes (#59)
* Translated descriptions for `Content-Crs` and `Accept-Crs` headers from Dutch to English in the OAS (#106)
* Added information about validation to the OAS (#106)


1.0.0 (2021-01-13)
------------------

🎉 First release of Objects API.
