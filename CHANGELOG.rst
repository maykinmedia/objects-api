==============
Change history
==============

1.1.0 (2021-04-21)
------------------

**Bugfixes and QOL**

* Improved performance with database query optimization (#136) :zap:
* Bumped to newer versions of Django, Jinja2, Pillow, PyYAML including security fixes (#183, #182, #184, #176, #193)

* Fixed a crash when creating an object without a version in the admin (#146)
* Fixes a crash when opening an objecttype without versions in the admin (maykinmedia/objects-api#144)

**Deployment tooling / infrastructure**

* Added Helm chart to deploy the Objects API on Kubernetes (#180)
* Added Ansible configuration to deploy the Objecttypes on single server (#59)

**Documentation**

* Added a tutorial how to use the Objects API and the Objecttypes API with examples (#61)
* Documented how to configure authentication and authorization for the Objects API and the Objecttypes API (#179)
* Documented deployment of the Objects API and the Objecttypes API on single server and Kubernetes (#59)
* Translated descriptions for `Content-Crs` and `Accept-Crs` headers from Dutch to English in the OAS (#106)
* Added information about validation to the OAS (#106)

**New features**

* Decoupled authentication tokens from users in the admin (#115)
* Added additional fields for tokens to store extra information (#155)
* For object types use special ObjectType object instead of urls (#115)

* Improved the Admin UI:

    * Include `uuid` field to the "object" page (#156)
    * Make `object_type` field immutable (#150)
    * Add filtering on `object_type` to the "object" page (#157)

* Adhere the Objecttypes API to API principles API-09, API-18, API-19, API-51 defined in API Design Rules of Nederlandse API Strategie (#46, #174)
* Support `fields=` query param and display only selected fields in the API response (#174)
* Add length validation fo url fields (#154)

**Cleanup**

* Updated to pip-tools 6 to pin/freeze dependency trees


1.0.0 (2021-01-13)
------------------

🎉 First release of Objects API.
