.. _installation_oidc:

============================
OpenID Connect configuration
============================

Objects API supports Single Sign On (SSO) using the OpenID Connect protocol (OIDC) for the admin interface.

Users can login to the Objects API admin interface, using their account registered by the OpenID Connect provider. In this flow:

1. The user clicks on *Login with organization account* in the login screen.
2. The user is redirected to the website of the OpenID Connect provider (i.e., Keycloak), where they log in with
   username and password (and possible Multi Factor Authentication).
3. The OIDC website sends the user back to Objects API (where the account for the user is created, if it does not yet exist).
4. An admin in Objects API assigns the account to the appropriate groups when the user logs in
   to their account for the first time.

.. note:: By default, the account is created, but it does **not** get access to the admin interface.
   These permissions must be configured by (another) admin.

.. _installation_oidc_appgroup:

Configuration of OIDC provider
==============================

Contact the IAM admins in your organization to create a *Client* in the environment
of the OpenID Connect provider

As **Redirect URI** enter ``https://objects.municipality.nl/oidc/callback``, where
``open-notificaties.municipality.nl`` is substituted with the relevant domain.

At the end of this process, the following data must be returned (on premise):

* Server addres, i.e., ``login.municipality.nl``
* Client ID, i.e., ``a7d14516-8b20-418f-b34e-25f53c930948``
* Client secret, i.e., ``97d663a9-3624-4930-90c7-2b90635bd990``

Configuration of OIDC in Objects API
====================================

Ensure you possess the following data:

* Server addres
* Client ID
* Client secret

Then, in the admin interface navigate to **Configuration** > **OpenID Connect configuration**.

1. Check *Enable* to enable OIDC.
2. For **OpenID Connect client ID** enter the Client ID, i.e.,
   ``a7d14516-8b20-418f-b34e-25f53c930948``.
3. For **OpenID Connect secret** enter the Client secret, i.e.,
   ``97d663a9-3624-4930-90c7-2b90635bd990``.
4. Leave the default value for **OpenID Connect scopes**.
5. For **OpenID sign algorithm** enter ``RS256``.
6. Leave **Sign key** blank.

Thereafter, a few endpoints belonging to the OIDC provider must be configured.
These can be derived automatically from the discovery endpoint
(``https://login.municipality.nl/auth/realms/{realm}/.well-known/openid-configuration``).

7. For **Discovery endpoint** enter the path to the correct authentication realm
   endpoint of the OpenID Connect provider (ending in a `/`), i.e.,
   ``https://login.municipality.nl/auth/realms/{realm}/``
8. Leave the remaining endpoints blank.

Finally, click the **Save** button in the bottom right corner.

The simplest way to test if OIDC authentication functions properly, is by navigating to
https://objects.municipality.nl/admin/ in an incognito window and clicking *Login with organization account*.
