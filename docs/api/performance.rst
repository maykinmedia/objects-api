===================
Performance
===================

To ensure good user experience and quality of execution, we have a dedicated `performance testing repository`_, it is run
on a system with the following specifications:

.. csv-table:: System specifications
   :widths: 20, 80
   :delim: :

    **Operating System**: Debian GNU/Linux 10 (buster) [x86_64 GNU/Linux]
    **RAM**: 4GB
    **CPU(s)**: x2 (Intel Xeon E312xx)
    **Hard drive**: 52GB

We run the tests after every major Objects API version and document the stats, this careful analysis allows us to meet high-quality standards.

.. csv-table:: Performance results (v2.0.0-alpha / latest)
   :header: "v2.0.0-alpha", "Average (ms)",	"Min (ms)",	"Max (ms)", "Average size (bytes)",	"RPS",	"Failures/s"
   :delim: ;

    GET;Retrieve by data_attrs;474;349;584;59724;0.1;0.0
    GET;Retrieve by date;436;383;534;59749;0.1;0.0
    GET;Retrieve by geo coordinates;432;389;474;59779;0.1;0.0
    GET;Retrieve by pageSize (100);389;389;389;59776;0.0;0.0
    GET;Retrieve by pageSize (150);460;415;510;89471;0.0;0.0
    GET;Retrieve by pageSize (25);357;336;376;15057;0.0;0.0
    GET;Retrieve by pageSize (250);592;502;678;148838;0.0;0.0
    GET;Retrieve by pageSize (5);327;327;327;3072;0.0;0.0
    GET;Retrieve by pageSize (50);363;361;365;29905;0.0;0.0
    GET;Retrieve by pageSize (500);828;793;864;297323;0.0;0.0
    GET;Retrieve by registrationDate;158;122;192;16565;0.1;0.0
    GET;Retrieve single object;103;88;124;1676;0.1;0.0

.. csv-table:: Tested requests
   :header: "#", "Method", "Type"
   :delim: ;

    1;GET;Retrieve by data_attrs
    2;GET;Retrieve by date
    3;GET;Retrieve by geo coordinates
    4;GET;Retrieve by pageSize (100)
    5;GET;Retrieve by pageSize (150)
    6;GET;Retrieve by pageSize (25)
    7;GET;Retrieve by pageSize (250)
    8;GET;Retrieve by pageSize (5)
    9;GET;Retrieve by pageSize (50)
    10;GET;Retrieve by pageSize (500)
    11;GET;Retrieve by registrationDate
    12;GET;Retrieve single object

.. _`performance testing repository`: https://github.com/maykinmedia/objects-api-performance
