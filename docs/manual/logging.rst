.. _manual_logging:

Logging
=======

Format Objects
--------------

Objects API emits structured logs (using `structlog <https://www.structlog.org/en/stable/>`_).
A log line can be formatted like this:

.. code-block:: json

    {
        "object_uuid":"1734afac-4628-446d-b344-f39b42f48bd9",
        "objecttype_uuid":"b427ef84-189d-43aa-9efd-7bb2c459e281",
        "objecttype_version":1,
        "token_identifier":"application-test",
        "token_application":"Application (test)",
        "event":"object_created",
        "user_id":null,
        "request_id":"2f9e9a5b-d549-4faa-a411-594aa8a52eee",
        "timestamp":"2025-05-19T14:09:20.339166Z",
        "logger":"objects.api.serializers",
        "level":"info"
    }

Format Objecttypes
------------------

Objecttypes API emits structured logs (using `structlog <https://www.structlog.org/en/stable/>`_).
A log line can be formatted like this:

.. code-block:: json

    {
        "uuid":"b427ef84-189d-43aa-9efd-7bb2c459e281",
        "naam":"test"
        "token_identifier":"application-test",
        "token_application":"Application (test)",
        "event":"objecttype_created",
        "user_id":null,
        "request_id":"2f9e9a5b-d549-4faa-a411-594aa8a52eee",
        "timestamp":"2025-05-19T14:09:20.339166Z",
        "logger":"objecttypes.api.v2.views",
        "level":"info"
    }

Each log line will contain an ``event`` type, a ``timestamp`` and a ``level``.
Dependent on your configured ``LOG_LEVEL`` (see :ref:`installation_env_config` for more information),
only log lines with of that level or higher will be emitted.

API log events
--------------

Below is the list of logging ``event`` types that Objects and Objecttypes API can emit. In addition to the mentioned
context variables, these events will also have the **request bound metadata** described in the :ref:`django-structlog documentation <request_events>`.

Objects API
~~~~~~~~~~~

* ``objecttypes_api_request_failure``: a request to the Objecttypes API has failed. Additional context: ``exc_info``.
* ``search_failed_for_datastore``: attempted to perform ``jsonpath`` search for a backend that does not support this operation. Additional context: ``exc_info``.
* ``object_created``: created an ``Object`` via the API. Additional context: ``object_uuid``, ``objecttype_uuid``, ``objecttype_version``, ``token_identifier``, ``token_application``.
* ``object_updated``: updated an ``Object`` via the API. Additional context: ``object_uuid``, ``objecttype_uuid``, ``objecttype_version``, ``token_identifier``, ``token_application``.

Objecttypes API
~~~~~~~~~~~~~~~

* ``objecttype_created``: created an ``Objecttype`` via the API. Additional context: ``uuid``, ``naam``, ``token_identifier``, ``token_application``.
* ``objecttype_updated``: updated an ``Objecttype`` via the API. Additional context: ``uuid``, ``naam``, ``token_identifier``, ``token_application``.
* ``objecttype_deleted``: deleted an ``Objecttype`` via the API. Additional context: ``uuid``, ``naam``, ``token_identifier``, ``token_application``.
* ``object_version_created``: created an ``Object_version`` via the API. Additional context: ``version``, ``objecttype_uuid``, ``token_identifier``, ``token_application``.
* ``object_version_updated``: updated an ``Object_version`` via the API. Additional context: ``version``, ``objecttype_uuid``, ``token_identifier``, ``token_application``.
* ``object_version_deleted``: deleted an ``Object_version`` via the API. Additional context: ``version``, ``objecttype_uuid``, ``token_identifier``, ``token_application``.

.. _manual_logging_exceptions:

Exceptions
----------

Handled exceptions follow a standardized JSON format to ensure consistency and improve error tracking.
Most fields are standard and include:
``title``, ``code``, ``status``, ``event``, ``source``, ``user_id``, ``request_id``, ``timestamp``, ``logger`` and ``level``.

A new field ``data`` has been added to provide detailed information about which input parameters caused the error in API calls.

.. code-block:: json

    {
        "title": "Authentication credentials were not provided.",
        "code": "not_authenticated",
        "status": 401,
        "data": {
            "detail": "Authentication credentials were not provided."
        },
        "event": "api.handled_exception",
        "user_id": null,
        "request_id": "68b46bf0-a5b8-43f7-a550-e37dee617bff",
        "source": "app",
        "timestamp": "2025-10-06T07:43:40.991929Z",
        "logger": "objects.utils.views",
        "level": "error"
    }

Uncaught exceptions that occur via the API are logged as ``api.uncaught_exception`` events
and contain the traceback of the exception.

.. code-block:: json

    {
        "event": "api.uncaught_exception",
        "request_id": "9a5c781d-b15c-4b3a-8910-e7968ae37cb6",
        "user_id": null,
        "timestamp": "2025-10-06T08:31:57.572352Z",
        "logger": "objects.utils.views",
        "level": "error",
        "exception": "Traceback (most recent call last):\n  File \"/usr/local/lib/python3.12/site-packages/rest_framework/views.py\", line 497, in dispatch\n    self.initial(request, *args, **kwargs)\n  File \"/usr/local/lib/python3.12/site-packages/vng_api_common/geo.py\", line 30, in initial\n    super().initial(request, *args, **kwargs)\n  File \"/usr/local/lib/python3.12/site-packages/rest_framework/views.py\", line 415, in initial\n    self.check_permissions(request)\n  File \"/usr/local/lib/python3.12/site-packages/rest_framework/views.py\", line 332, in check_permissions\n    if not permission.has_permission(request, self):\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/app/src/objects/token/permissions.py\", line 10, in has_permission\n    1 / 0\n    ~~^~~\nZeroDivisionError: division by zero"
    }


Setup configuration
-------------------

* ``no_permissions_defined``: while running the token configuration step, it was detected that neither permissions nor ``is_superuser`` was set for the token. Additional context: ``token_identifier``.
* ``no_tokens_defined``: while running the token configuration step, it was detected that the config file did not define any tokens.
* ``configuring_token``: attempting to configure a token. Additional context: ``token_identifier``.
* ``save_token_to_database``: attempting to save a token to the database. Additional context: ``token_identifier``.
* ``token_configuration_failure``: configuring a token failed. Additional context: ``token_identifier``, ``exc_info``.
* ``token_configuration_success``: configuring a token succeeded. Additional context: ``token_identifier``.

Data migrations
---------------

* ``token_identifier_generated``: while migrating, an ``identifier`` was generated for a token. Additional context: ``token_identifier``, ``token_pk``.
* ``missing_service_for_objecttype``: while migrating, a ``Service`` object is missing for an ``ObjectType``. Additional context: ``object``, ``objecttype``.
* ``invalid_objecttype``: while migrating, the ``ObjectType`` is not valid, because it was not possible to parse a UUID from it. Additional context: ``object``, ``objecttype``.

Third party library events
--------------------------

For more information about log events emitted by third party libraries, refer to the documentation
for that particular library

* :ref:`Django (via django-structlog) <request_events>`
* :ref:`Celery (via django-structlog) <request_events>`
