.. _manual_logging:

Logging
=======

Format
------

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

Each log line will contain an ``event`` type, a ``timestamp`` and a ``level``.
Dependent on your configured ``LOG_LEVEL`` (see :ref:`installation_env_config` for more information),
only log lines with of that level or higher will be emitted.

Objects API log events
----------------------

Below is the list of logging ``event`` types that Objects API can emit.

API
~~~

* ``objecttypes_api_request_failure``: a request to the Objecttypes API has failed. Additional context: ``exc_info``.
* ``search_failed_for_datastore``: attempted to perform ``jsonpath`` search for a backend that does not support this operation. Additional context: ``exc_info``.
* ``object_created``: created an ``Object`` via the API. Additional context: ``object_uuid``, ``objecttype_uuid``, ``objecttype_version``, ``token_identifier``, ``token_application``.
* ``object_updated``: updated an ``Object`` via the API. Additional context: ``object_uuid``, ``objecttype_uuid``, ``objecttype_version``, ``token_identifier``, ``token_application``.

Setup configuration
~~~~~~~~~~~~~~~~~~~

* ``no_permissions_defined``: while running the token configuration step, it was detected that neither permissions nor ``is_superuser`` was set for the token. Additional context: ``token_identifier``.
* ``no_tokens_defined``: while running the token configuration step, it was detected that the config file did not define any tokens.
* ``configuring_token``: attempting to configure a token. Additional context: ``token_identifier``.
* ``save_token_to_database``: attempting to save a token to the database. Additional context: ``token_identifier``.
* ``token_configuration_failure``: configuring a token failed. Additional context: ``token_identifier``, ``exc_info``.
* ``token_configuration_success``: configuring a token succeeded. Additional context: ``token_identifier``.

Data migrations
~~~~~~~~~~~~~~~

* ``token_identifier_generated``: while migrating, an ``identifier`` was generated for a token. Additional context: ``token_identifier``, ``token_pk``.
* ``missing_service_for_objecttype``: while migrating, a ``Service`` object is missing for an ``ObjectType``. Additional context: ``object``, ``objecttype``.
* ``invalid_objecttype``: while migrating, the ``ObjectType`` is not valid, because it was not possible to parse a UUID from it. Additional context: ``object``, ``objecttype``.

Third party library events
--------------------------

For more information about log events emitted by third party libraries, refer to the documentation
for that particular library

* :ref:`Django (via django-structlog) <request_events>`
* :ref:`Celery (via django-structlog) <request_events>`
