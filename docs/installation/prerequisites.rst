.. _installation_prerequisites:

Prerequisites
=============

Objects API and Objecttypes API are most often deployed as a Docker containers. While the
`Objects API container images <https://hub.docker.com/r/maykinmedia/objects-api/>`_ /
`Objecttypes API container images <https://hub.docker.com/r/maykinmedia/objecttypes-api/>`_ contain all the
necessary dependencies, both components require extra services to deploy the full stack.
These dependencies and their supported versions are documented here.

The ``docker-compose.yml`` (not suitable for production usage!) in the root of the
repository also describes these dependencies.

PostgreSQL with Postgis
-----------------------

.. warning::

   Since Objects API version 3.0.4 and Objecttypes API version 3.0.4,
   PostgreSQL version 14 or higher is required. Attempting to deploy these versions
   with PostgreSQL 13 or lower will result in errors!

Objects API and Objecttypes API currently only support PostgreSQL as datastore. The Objects API is geo-capable,
which requires the postgis_ extension to be enabled.

The supported versions in the table below are tested in the CI pipeline.

============ ==================== ============ ============ ============ ============
Matrix       Postgres 13 or lower Postgres 14  Postgres 15  Postgres 16  Postgres 17
============ ==================== ============ ============ ============ ============
Postgis 3.2  |cross|              |check|      |cross|      |cross|      |cross|
Postgis 3.5  |cross|              |check|      |check|      |check|      |check|
============ ==================== ============ ============ ============ ============

.. warning:: Both components only support maintained versions of PostgreSQL. Once a version is
   `EOL <https://www.postgresql.org/support/versioning/>`_, support will
   be dropped in the next release.

.. _postgis: https://postgis.net/

Redis
-----

Both components use Redis as a cache backend, especially relevant for admin sessions, and as
task queue broker.

Supported versions: 5, 6, 7.

.. |check| unicode:: U+2705 .. ✅
.. |cross| unicode:: U+274C .. ❌
