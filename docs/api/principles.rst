.. _api_principles:

==============
API principles
==============

The Objects API and Objecttypes API are designed to adhere to API principles
defined in `API Designrules`_, which is a part of `Nederlandse API Strategie`_.

.. csv-table:: Adherence to API principles
   :header: "#", "Principle", "Objects API", "Objecttypes API"
   :widths: 10, 30, 30, 30

   API-01,Operations are Safe and/or Idempotent,"Yes, with exception of PUT",Yes
   API-02,Do not maintain state information at the server,Yes,Yes
   API-03,Only apply default HTTP operations,Yes,Yes
   API-04,Define interfaces in Dutch unless there is an official English glossary,"No, Objects API has English interface","No, Objecttypes API has English interface"
   API-05,Use plural nouns to indicate resources,Yes,Yes
   API-06,Create relations of nested resources within the endpoint,"N/a, there are no nested resources","N/a, there are no nested resources"
   API-09,Implement custom representation if supported,No,No
   API-10,Implement operations that do not fit the CRUD model as sub-resources,Yes,Yes
   API-16,Use OAS 3.0 for documentation,Yes,Yes
   API-17,Publish documentation in Dutch unless there is existing documentation in English or there is an official English glossary available,"No, Objects API has English documentation","No, Objecttypes API has English documentation"
   API-18,Include a deprecation schedule when publishing API changes,No,No
   API-19,Allow for a maximum 1 year transition period to a new API version,"N/a, new API version is not expected","N/a, new API version is not expected"
   API-20,API-20: Include the major version number only in ihe URI,Yes,Yes
   API-48,Leave off trailing slashes from API endpoints,Yes,Yes
   API-51,Publish OAS at the base-URI in JSON-format,No,No


.. _`API Designrules`: https://docs.geostandaarden.nl/api/API-Designrules/
.. _`Nederlandse API Strategie`: https://docs.geostandaarden.nl/api/API-Strategie/
