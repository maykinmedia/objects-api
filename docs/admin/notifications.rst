.. _admin_notifications:

=============
Notifications
=============

The Objects API can be configured to send notifications to a configured Notificaties API.
These notifications are sent whenever Objects are created, updated or deleted via the Objects API.
Other applications can subscribe to these notifications, for example to trigger
certain processes whenever an Object is created.

For more information on the Notificaties API, please refer to the `documentation`_.

Configuration
=============

In order to configure notifications, navigate to the admin page and click on the
"change" button next to "Notificatiescomponentconfiguratie", under the "Configuration" tab.

.. image:: _assets/img/notifications_admin_index.png
    :alt: Click on the "change" button next to "Notificatiescomponentconfiguratie"

On the next page, fill in the correct API root of the Notificaties API to which
notifications must be sent and click on the "save" button afterwards.

.. image:: _assets/img/notifications_admin_config.png
    :alt: Fill in the correct API root and click on the "save" button

Navigate back to the admin index page and click on the "add" button next to
"Services", under the "Configuration" tab.

.. image:: _assets/img/notifications_admin_index_2.png
    :alt: Click on the "add" button next to "Services"

On the "add service" page, fill in the following information:

1. **Label**: the name of the **Service**, i.e. ``Notificaties API``
2. **Type**: ``NRC (Notifications``
3. **Api root url**: the same URL as in the "Notificatiescomponentconfiguratie"
4. **Client ID**: a valid client ID to identify the Objects API (registered in Autorisaties API)
5. **Secret**: a secret corresponding to the client ID (registered in Autorisaties API)
6. **Authorization type**: ``ZGW client_id + secret``
7. **Header key** / **Header value**: leave empty
8. **OAS**: a URL pointing to the OpenAPI specification of the Notificaties API,
   the API root from step 2, followed by ``schema/openapi.yaml``
9. **Nlx url**: leave empty
10. **User ID**: a user ID to show in the audittrail
11. **User representation**: a human readable representation of this application
    to show in the audittrail

Finally, click on the "save" button.

.. image:: _assets/img/notifications_service_add.png
    :alt: Click on the "add" button next to "Services"

In order for this configuration to work, API authorizations must be configured
in an Autorisaties API. Open Zaak is an example of an application that implements this API.
For more information on how to configure API authorizations in Open Zaak,
please refer to the `Open Zaak authorization documentation`_.

For more information on how to set up subscriptions in Open Notificaties, please refer
to the `Open Notificaties subscription documentation`_.

Automatic retry for notifications
=================================

By default, sending notifications has automatic retry behaviour, i.e. if the notification
publishing task has failed, it will automatically be rescheduled/tried again until the maximum
retry limit has been reached.

Autoretry explanation and configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Retry behaviour is implemented using binary exponential backoff with a delay factor,
the formula to calculate the time to wait until the next retry is as follows:

.. math::

    t = \text{backoff_factor} * 2^c

where `t` is time in seconds and  `c` is the number of retries that have been performed already.

In the **Configuratie > Notificatiescomponentconfiguratie** admin page the autoretry settings
can be configured:

* **Notification delivery max retries**: the maximum number of retries the task queue
  will do if sending a notification has failed. Default is ``5``.
* **Notification delivery retry backoff**: a boolean or a number. If this option is set to
  ``True``, autoretries will be delayed following the rules of binary exponential backoff. If
  this option is set to a number, it is used as a delay factor. Default is ``3``.
* **Notification delivery retry backoff max**: an integer, specifying number of seconds.
  If ``Notification delivery retry backoff`` is enabled, this option will set a maximum
  delay in seconds between task autoretries. Default is ``48`` seconds.

With the assumption that the requests are done immediately we can model the notification
tasks schedule with the default configurations:

1. At 0s the request to create an Object is made, the notification task is scheduled, picked up
   by worker and failed
2. At 3s with 3s delay the first retry happens (``2^0`` * ``Notification delivery retry backoff``)
3. At 9s with 6s delay - the second retry (``2^1`` * ``Notification delivery retry backoff``)
4. At 21s with 12s delay - the third retry
5. At 45s with 24s delay - the fourth retry
6. At 1m33s with 48s delay - the fifth retry, which is the last one.

So if the Notification API is up after 1 min of downtime the default configuration can handle it
automatically.

.. _documentation: https://open-notificaties.readthedocs.io
.. _Open Zaak authorization documentation: https://open-zaak.readthedocs.io/en/stable/manual/api-authorizations.html
.. _Open Notificaties subscription documentation: https://open-notificaties.readthedocs.io/en/stable/manual/subscriptions.html
