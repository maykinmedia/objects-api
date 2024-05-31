.. _installation_quickstart:

Quickstart
==========

A simple ``docker-compose.yml`` file is available to get the APIs
up and running in minutes. This file has some convenience settings to get
started quickly and these should never be used for anything besides testing:

* A default secret is set in the ``SECRET_KEY`` environment variable.
* A predefined database and database account is used.
* API authorizations are disabled.

With the above remarks in mind, let's go:

Objecttypes API
---------------

1. Create a project folder:

   .. code:: shell

      $ mkdir objecttypes-api
      $ cd objecttypes-api

2. Download the ``docker-compose`` file:

   .. tabs::

      .. tab:: Linux

         .. code:: shell

            $  wget https://raw.githubusercontent.com/maykinmedia/objecttypes-api/master/docker-compose.yml

      .. tab:: Windows Powershell 3

         .. code:: shell

            PS> wget https://raw.githubusercontent.com/maykinmedia/objecttypes-api/master/docker-compose.yml

3. Start the Docker containers:

   .. code:: shell

      $ docker compose up -d --no-build

4. Import a demo set of objecttypes:

   .. code:: shell

      $ docker compose exec web src/manage.py loaddata demodata

5. Create a superuser

   .. code:: shell

      $ docker compose exec web src/manage.py createsuperuser


Objects API
-----------

1. Create a project folder:

   .. code:: shell

      $ mkdir objects-api
      $ cd objects-api

2. Download the ``docker-compose`` file:

   .. tabs::

      .. tab:: Linux

         .. code:: shell

            $ wget https://raw.githubusercontent.com/maykinmedia/objects-api/master/docker-compose.yml

      .. tab:: Windows Powershell 3

         .. code:: shell

            PS> wget https://raw.githubusercontent.com/maykinmedia/objects-api/master/docker-compose.yml

3. Start the Docker containers:

   .. code:: shell

      $ docker compose -f docker-compose-qs.yml up -d --no-build

4. Import a demo set of objects (linking to the demo objecttypes):

   .. code:: shell

      $ docker compose exec web src/manage.py loaddata demodata


5. Create a superuser

   .. code:: shell

      $ docker compose exec web src/manage.py createsuperuser


6. Retrieve an object via the Objects API in your webbrowser:

   .. code::

      http://localhost:8000/api/v1/objects/


After you have the Objects API and the Objecttypes API running you can configure
:ref:`admin_authentication`, :ref:`admin_authorization` and use the API's.
