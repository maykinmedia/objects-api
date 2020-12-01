===========
Objects API
===========

:Version: 0.1.0
:Source: https://github.com/maykinmedia/objects-api
:Keywords: objects, assets, zaakobjecten

|docs|

API to manage objects belonging to a certain object type.
(`Nederlandse versie`_)

Developed by `Maykin Media B.V.`_ commissioned by the Municipality of Utrecht.


Introduction
============

The Objects API aims to easily store various objects and make them available in
standardized format. The Objects API can be used by any organization to manage
relevant objects. An organization can also choose to use the Objects API to
expose objects to the public, as Open Data.

To define the format of objects, so called object types, organizations can use
a national and/or local `Objecttypes API`_.


API specification
=================

|lint-oas| |generate-sdks| |generate-postman-collection|

==============  ==============  =============================
Version         Release date    API specification
==============  ==============  =============================
1.0.0-alpha     n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/master/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/master/src/openapi.yaml>`_
==============  ==============  =============================

See: `All versions and changes <https://github.com/maykinmedia/objects-api/blob/master/CHANGELOG.rst>`_


Reference implementation
========================

|build-status| |coverage| |black| |docker| |python-versions|

The reference implementation is used to demonstrate the API in action and can 
be used for test and demo purposes. The reference implementation is open source,
well tested and available as Docker image.

Quickstart
----------

1. Download and run the Objects API:

   .. code:: bash

      $ wget https://raw.githubusercontent.com/maykinmedia/objects-api/master/docker-compose-quickstart.yml -O docker-compose.yml
      $ docker-compose up -d
      $ docker-compose exec web src/manage.py createsuperuser

2. In the browser, navigate to ``http://localhost:8000/`` to access the admin 
   and the API.


References
==========

* `Documentation <https://readthedocs.org/projects/objects-and-objects-api/badge/?version=latest>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/objects-api>`_
* `Issues <https://github.com/maykinmedia/objects-api/issues>`_
* `Code <https://github.com/maykinmedia/objects-api>`_
* `Community <https://commonground.nl/groups/view/54477963/objecten-en-objecttypen-api>`_


License
=======

Copyright © Maykin Media, 2020

Licensed under the EUPL_


.. _`Nederlandse versie`: README.NL.rst

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl

.. _`Objecttypes API`: https://github.com/maykinmedia/objecttypes-api

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://travis-ci.com/maykinmedia/objects-api.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.com/maykinmedia/objects-api

.. |docs| image:: https://readthedocs.org/projects/objects-and-objecttypes-api/badge/?version=latest
    :target: https://objects-and-objecttypes-api.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |coverage| image:: https://codecov.io/github/maykinmedia/objects-api/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/maykinmedia/objects-api

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |docker| image:: https://images.microbadger.com/badges/image/maykinmedia/objects-api.svg
    :alt: Docker image
    :target: https://hub.docker.com/r/maykinmedia/objects-api

.. |python-versions| image:: https://img.shields.io/badge/python-3.7%2B-blue.svg
    :alt: Supported Python version

.. |lint-oas| image:: https://github.com/maykinmedia/objects-api/workflows/lint-oas/badge.svg
    :alt: Lint OAS
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Alint-oas

.. |generate-sdks| image:: https://github.com/maykinmedia/objects-api/workflows/generate-sdks/badge.svg
    :alt: Generate SDKs
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Agenerate-sdks

.. |generate-postman-collection| image:: https://github.com/maykinmedia/objects-api/workflows/generate-postman-collection/badge.svg
    :alt: Generate Postman collection
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Agenerate-postman-collection
