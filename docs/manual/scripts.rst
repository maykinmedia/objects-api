
.. _scripts:

Scripts
=======

Dump data
---------

Met het script ``dump_data.sh`` kan de data van alle componenten (core) worden geëxporteerd naar een sql bestand.

Dit script is niet bedoeld voor een data migratie naar een andere Objects Api of Objecttypes Api instantie.

Standaard wordt het volledige schema en data in twee sql bestanden gegenereerd. dit kan worden aangepast via de flags ``--data-only``, ``--schema-only`` & ``--combined``
waardoor een bestand wordt gegenereerd. De data dump bevat standaard alle core data.
Om alleen specifieke data te exporteren kunnen de gewenste component namen worden meegegeven:

.. code-block:: shell

    ./dump_data.sh core

.. note::

    om een postgres 17 db te exporteren is de package postgres-client-17 vereist.

Environment variabelen
----------------------

* DB_HOST (db)
* DB_PORT (5432)
* DB_USER (objects/objecttypes)
* DB_NAME (objects/objecttypes)
* DB_PASSWORD ("")
* DUMP_FILE ("dump_$(date +'%Y-%m-%d_%H-%M-%S').sql")

.. code-block:: shell

    DB_HOST=localhost DB_NAME=objects ./bin/dump_data.sh
