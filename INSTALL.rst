============
Installation
============

The project is developed in Python using the `Django framework`_. There are 3
sections below, focussing on developers, running the project using Docker and
hints for running the project in production.

.. _Django framework: https://www.djangoproject.com/


Development
===========


Prerequisites
-------------

You need the following libraries and/or programs:

* `Python`_ 3.11 or above
* Python `Virtualenv`_ and `Pip`_
* `PostgreSQL`_ 14 or above with PostGIS extension
* `Node.js`_
* `npm`_

.. _Python: https://www.python.org/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _Pip: https://packaging.python.org/tutorials/installing-packages/#ensure-pip-setuptools-and-wheel-are-up-to-date
.. _PostgreSQL: https://www.postgresql.org
.. _Node.js: http://nodejs.org/
.. _npm: https://www.npmjs.com/


Getting started
---------------

Developers can follow the following steps to set up the project on their local
development machine.

1. Navigate to the location where you want to place your project.

2. Get the code:

   .. code-block:: bash

       $ git clone git@github.com:maykinmedia/objects-api.git
       $ cd objects-api

3. Install all required (backend) libraries.

   .. code-block:: bash

       $ virtualenv env
       $ source env/bin/activate
       $ pip install -r requirements/dev.txt
       $ pre-commit install

4. Install all required (frontend) libraries and build static files.

   .. code-block:: bash

       $ npm install
       $ npm run build

5. Activate your virtual environment and create the statics and database:

   .. code-block:: bash

       $ source env/bin/activate
       $ python src/manage.py collectstatic --link
       $ python src/manage.py migrate

6. Create a superuser to access the management interface:

   .. code-block:: bash

       $ python src/manage.py createsuperuser

7. You can now run your installation and point your browser to the address
   given by this command:

   .. code-block:: bash

       $ python src/manage.py runserver

8. Create a .env file with database settings. See dotenv.example for an example.

        $ cp dotenv.example .env


**Note:** If you are making local, machine specific, changes, add them to
``src/objects/conf/local.py``. You can base this file on the
example file included in the same directory.


.. _ECMA: https://ecma-international.org/
.. _Sass: https://sass-lang.com/


Update installation
-------------------

When updating an existing installation:

1. Activate the virtual environment:

   .. code-block:: bash

       $ cd objects
       $ source env/bin/activate

2. Update the code and libraries:

   .. code-block:: bash

       $ git pull
       $ pip install -r requirements/dev.txt
       $ npm install
       $ npm run build

3. Update the statics and database:

   .. code-block:: bash

       $ python src/manage.py collectstatic --link
       $ python src/manage.py migrate


Testsuite
---------

To run the test suite:

.. code-block:: bash

    $ python src/manage.py test objects

Configuration via environment variables
---------------------------------------

A number of common settings/configurations can be modified by setting
environment variables. You can persist these in your ``local.py`` settings
file or as part of the ``(post)activate`` of your virtualenv.

* ``SECRET_KEY``: the secret key to use. A default is set in ``dev.py``

* ``DB_NAME``: name of the database for the project. Defaults to ``objects``.
* ``DB_USER``: username to connect to the database with. Defaults to ``objects``.
* ``DB_PASSWORD``: password to use to connect to the database. Defaults to ``objects``.
* ``DB_HOST``: database host. Defaults to ``localhost``
* ``DB_PORT``: database port. Defaults to ``5432``.

* ``SENTRY_DSN``: the DSN of the project in Sentry. If set, enabled Sentry SDK as
  logger and will send errors/logging to Sentry. If unset, Sentry SDK will be
  disabled.

Docker
======

The easiest way to get the project started is by using `Docker Compose`_.

1. Clone or download the code from `Github`_ in a folder like
   ``objects``:

   .. code-block:: bash

       $ git clone git@github.com:maykinmedia/objects-api.git
       Cloning into 'objects'...
       ...

       $ cd objects

2. Start the database and web services:

   .. code-block:: bash

       $ docker-compose up -d
       Starting objects-api_db_1 ... done
       Starting objects-api_web_1 ... done

   It can take a while before everything is done. Even after starting the web
   container, the database might still be migrating. You can always check the
   status with:

   .. code-block:: bash

       $ docker logs -f objects-api_web_1

3. Create an admin user and load initial data. If different container names
   are shown above, use the container name ending with ``_web_1``:

   .. code-block:: bash

       $ docker exec -it objects-api_web_1 /app/src/manage.py createsuperuser
       Username: admin
       ...
       Superuser created successfully.

       $ docker exec -it objects-api_web_1 /app/src/manage.py loaddata admin_index groups
       Installed 5 object(s) from 2 fixture(s)

4. Point your browser to ``http://localhost:8000/`` to access the project's
   management interface with the credentials used in step 3.

   If you are using ``Docker Machine``, you need to point your browser to the
   Docker VM IP address. You can get the IP address by doing
   ``docker-machine ls`` and point your browser to
   ``http://<ip>:8000/`` instead (where the ``<ip>`` is shown below the URL
   column):

   .. code-block:: bash

       $ docker-machine ls
       NAME      ACTIVE   DRIVER       STATE     URL
       default   *        virtualbox   Running   tcp://<ip>:<port>

5. To shutdown the services, use ``docker-compose down`` and to clean up your
   system you can run ``docker system prune``.

.. _Docker Compose: https://docs.docker.com/compose/install/
.. _Github: https://github.com/maykinmedia/objects/


More Docker
-----------

If you just want to run the project as a Docker container and connect to an
external database, you can build and run the ``Dockerfile`` and pass several
environment variables. See ``src/objects/conf/docker.py`` for
all settings.

.. code-block:: bash

    $ docker build -t objects
    $ docker run \
        -p 8000:8000 \
        -e DATABASE_USERNAME=... \
        -e DATABASE_PASSWORD=... \
        -e DATABASE_HOST=... \
        --name objects \
        objects

    $ docker exec -it objects /app/src/manage.py createsuperuser


Settings
========

All settings for the project can be found in
``src/objects/conf``.
The file ``local.py`` overwrites settings from the base configuration.


Commands
========

Commands can be executed using:

.. code-block:: bash

    $ python src/manage.py <command>

There are no specific commands for the project. See
`Django framework commands`_ for all default commands, or type
``python src/manage.py --help``.

.. _Django framework commands: https://docs.djangoproject.com/en/dev/ref/django-admin/#available-commands
