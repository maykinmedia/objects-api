===================
Performance
===================

To ensure good user experience and quality of performance, we have a dedicated `performance testing repository`_. It runs on a system with the following specifications:

.. csv-table:: System specifications
   :widths: 20, 80
   :delim: :

    **Operating System**: Debian GNU/Linux 10 (buster) [x86_64 GNU/Linux]
    **RAM**: 4GB
    **CPU(s)**: x2 (Intel Xeon E312xx)
    **Hard drive**: 52GB

The tests run under the following conditions:

* 500 total objects are used to ensure compatibility across older versions without pagination.
* 4 unique objecttypes.
* A single user simulates requests for a duration of 5 minutes.

We run the tests after every major version of the Objects API.
After that, we report and document the stats. This careful analysis allows us to showcase our high-quality optimization process.

Results
_______


.. csv-table:: Performance results per version (30 minutes)
   :header: "Method", "Test", "v2.0.0-alpha", "v1.1.1", "v1.1.0"
   :delim: ;

    GET;Retrieve all objects (ms);127;127;125
    GET;Retrieve by data_attrs (ms);117;111;115
    GET;Retrieve by date (ms);129;128;127
    GET;Retrieve by geo coordinates (ms);127;128;127
    GET;Retrieve by registrationDate (ms);130;131;130
    GET;Retrieve by single object (ms);106;106;109
    ;Aggregated;**123**;**122**;**122**

All performance reports are available for download for all versions:

- :download:`v2.0.0-alpha <_assets/v2.0.0-alpha.html>`
- :download:`v1.1.1 <_assets/v1.1.1.html>`
- :download:`v1.1.0 <_assets/v1.1.0.html>`

.. _`performance testing repository`: https://github.com/maykinmedia/objects-api-performance
