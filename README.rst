===========
Objects API
===========

:Version: 2.0.0
:Source: https://github.com/maykinmedia/objects-api
:Keywords: objects, assets, zaakobjecten

|docs|

API to manage objects belonging to a certain object type.
(`Nederlandse versie`_)

Developed by `Maykin Media B.V.`_ commissioned by the Municipality of Utrecht.


Introduction
============

The Objects API aims to easily store various objects and make them available in
standardized format. It can be used by any organization to manage
relevant objects. An organization can also choose to use it to
expose objects to the public as *Open Data*.

To define the format of objects, so called object types, organizations can use
a national and/or local `Objecttypes API`_.


API specification
=================

|lint-oas| |generate-sdks| |generate-postman-collection|

==============  ==============  =============================
Version         Release date    API specification
==============  ==============  =============================
latest          n/a             `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/master/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/master/src/objects/api/v2/openapi.yaml>`_,
                                (`diff <https://github.com/maykinmedia/objects-api/compare/2.0.0..master#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
2.0.0           2021-09-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.0.0/src/objects/api/v2/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/2.0.0/src/objects/api/v2/openapi.yaml>`_
                                (`diff <https://github.com/maykinmedia/objects-api/compare/1.2.0..2.0.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.2.0           2021-09-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.2.0/src/objects/api/v1/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.2.0/src/objects/api/v1/openapi.yaml>`_
                                (`diff <https://github.com/maykinmedia/objects-api/compare/1.1.1..1.2.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.1.1           2021-06-22      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.1/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.1/src/openapi.yaml>`_
                                (`diff <https://github.com/maykinmedia/objects-api/compare/1.1.0..1.1.1#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.1.0           2021-04-21      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.1.0/src/openapi.yaml>`_
                                (`diff <https://github.com/maykinmedia/objects-api/compare/1.0.0..1.1.0#diff-b9c28fec6c3f3fa5cff870d24601d6ab7027520f3b084cc767aefd258cb8c40a>`_)
1.0.0           2021-01-13      `ReDoc <https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.0.0/src/openapi.yaml>`_,
                                `Swagger <https://petstore.swagger.io/?url=https://raw.githubusercontent.com/maykinmedia/objects-api/1.0.0/src/openapi.yaml>`_
==============  ==============  =============================

Previous versions are supported for 6 month after the next version is released.

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

      $ wget https://raw.githubusercontent.com/maykinmedia/objects-api/master/docker-compose-quickstart.yml -O docker-compose-qs.yml
      $ docker-compose -f docker-compose-qs.yml up -d
      $ docker-compose exec web src/manage.py loaddata demodata
      $ docker-compose exec web src/manage.py createsuperuser

2. In the browser, navigate to ``http://localhost:8000/`` to access the admin
   and the API.


References
==========

* `Documentation <https://objects-and-objecttypes-api.readthedocs.io/>`_
* `Docker image <https://hub.docker.com/r/maykinmedia/objects-api>`_
* `Issues <https://github.com/maykinmedia/objects-api/issues>`_
* `Code <https://github.com/maykinmedia/objects-api>`_
* `Community <https://commonground.nl/groups/view/54477963/objecten-en-objecttypen-api>`_


License
=======

Copyright © Maykin Media, 2020 - 2021

Licensed under the EUPL_


.. _`Nederlandse versie`: README.NL.rst

.. _`Maykin Media B.V.`: https://www.maykinmedia.nl

.. _`Objecttypes API`: https://github.com/maykinmedia/objecttypes-api

.. _`EUPL`: LICENSE.md

.. |build-status| image:: https://github.com/maykinmedia/objects-api/workflows/ci/badge.svg?branch=master
    :alt: Build status
    :target: https://github.com/maykinmedia/objects-api/actions?query=workflow%3Aci

.. |docs| image:: https://readthedocs.org/projects/objects-and-objecttypes-api/badge/?version=latest
    :target: https://objects-and-objecttypes-api.readthedocs.io/
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
