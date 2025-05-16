.. _compliancy_api-strategy:

=======================
API strategy compliancy
=======================

The Objects API and Objecttypes API are designed to adhere to API principles
defined in `API Designrules`_, which is a part of `Nederlandse API Strategie`_.

.. csv-table:: Adherence to API principles
   :header: "#", "Principle", "Objects API", "Objecttypes API"
   :widths: 10, 40, 25, 25

   API-01,Operations are Safe and/or Idempotent,"Yes, with exception of PUT",Yes
   API-02,Do not maintain state information at the server,Yes,Yes
   API-03,Only apply default HTTP operations,Yes,Yes
   API-04,Define interfaces in Dutch unless there is an official English glossary,"No, Objects API has English interface","No, Objecttypes API has English interface"
   API-05,Use plural nouns to indicate resources,Yes,Yes
   API-06,Create relations of nested resources within the endpoint,"N/a, there are no nested resources",Yes
   API-09,Implement custom representation if supported,Yes,No
   API-10,Implement operations that do not fit the CRUD model as sub-resources,Yes,Yes
   API-16,Use OAS 3.0 for documentation,Yes,Yes
   API-17,Publish documentation in Dutch unless there is existing documentation in English or there is an official English glossary available,"No, Objects API has English documentation","No, Objecttypes API has English documentation"
   API-18,Include a deprecation schedule when publishing API changes,Yes,Yes
   API-19,Allow for a maximum 1 year transition period to a new API version,Yes (6 month),Yes (6 month)
   API-20,API-20: Include the major version number only in ihe URI,Yes,Yes
   API-48,Leave off trailing slashes from API endpoints,Yes,Yes
   API-51,Publish OAS at the base-URI in JSON-format,Yes,Yes


.. _`API Designrules`: https://docs.geostandaarden.nl/api/API-Designrules/
.. _`Nederlandse API Strategie`: https://docs.geostandaarden.nl/api/API-Strategie/
