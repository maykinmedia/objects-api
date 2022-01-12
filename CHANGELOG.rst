==============
Change history
==============

2.1.0 (2022-01-12)
------------------

**Component changes**

* **Bugfixes and QOL**

  * managed 2FA authentication using environment variables (#250)
  * integrated with OpenID Connect (#246)
  * create initial superuser with environment variables (#254)
  * removed non-actual results when filtering on `data_attr` query param (#260)
  * supported objecttypes with json schemas without properties in the Objects Admin (#273)
  * bumped to newer versions of mozilla-django-oidc-db (#264)

* **Deployment tooling / infrastructure**

  * use ansible collections from Ansible Galaxy (#241)

**API 1.3.0 changes**

* **New features**

  * supported numeric values for `icontains` query param (#262)
  * supported validation on `hasGeometry` field in the Objecttypes API (#263)

**API 2.1.0 changes**

* **New features**

  * supported numeric values for `icontains` query param (#262)
  * supported validation on `hasGeometry` field in the Objecttypes API (#263)
  * supported `ordering` query param which allows to sort the results (#274)


2.0.0 (2021-09-22)
------------------

**Component changes**

* Supports API 2.0.0 and API 1.2.0

**API 1.2.0 changes**

* **New features**

  * supported having several API versions at the same time (#195)
  * enabled selecting set of fields for every object type version which are allowed to display in the API (#79)
  * sent notifications when the objects are changed in the API using Notificaties API. Sending notifications is an optional feature that can be disabled (#221, #237)
  * added an endpoint to show which API permissions the client has (#81)
  * made `geometry` field non-required for the `search` endpoint (#236)
  * supported dates in the `data_attrs=` query param (#214)
  * supported `icontains` operator in the `data_attrs=` query param, which allows case-insensitive search on the part of the string (#235)
  * added two-factor authentication for the Objects Admin (#232)

* **Bugfixes and QOL**

  * bumped to newer versions of django, django-debug-toolbar, urllib3, sqlparse (#225, #243)
  * added superuser for quick-start (#203)
  * tested the performance of the API per version (#219)

* **Documentation**

  * marked read-only fields as non-required in OAS (#210)
  * described how to configure authorization with the set of allowed fields in the admin (#79)
  * documented how to configure notifications (#245)

**API 2.0.0 changes**

* **Breaking features**

  * paginated API responses (#148)

* **New features**

  * supported `data_icontains` query param which requires Postgres 12+ (#235)

* **Deployment tooling / infrastructure**

  * updated Postgres version in the Objects API Helm chart (#242)


1.1.1 (2021-06-22)
------------------

**Bugfixes and QOL**

* Fixed OAS generation: remove unrelated error response bodies and headers, swap the notion of material and formal history (#197, #201)
* Tested the implementation of the material and formal history (#168)

**Documentation**

* Documented how to use the Objecttypes admin and the Objects admin (#60)


1.1.0 (2021-04-21)
------------------

**New features**

* Decoupled authentication tokens from users in the admin (#115)
* Added additional fields for tokens to store extra information (#155)
* Adhered the Objecttypes API to API principles API-09, API-18, API-19, API-51 defined in API Design Rules of Nederlandse API Strategie (#46, #174)
* Supported `fields=` query param and display only selected fields in the API response (#174)
* Added length validation fo url fields (#154)
* Improved the Admin UI:

  * Include `uuid` field to the "object" page (#156)
  * Make `object_type` field immutable (#150)
  * Add filtering on `object_type` to the "object" page (#157)

**Bugfixes and QOL**

* Improved performance with database query optimization (#136) :zap:
* Bumped to newer versions of Django, Jinja2, Pillow, PyYAML, pip-tools including security fixes (#183, #182, #184, #176, #193)
* Fixed a crash when creating an object without a version in the admin (#146)

**Deployment tooling / infrastructure**

* Added Helm chart to deploy the Objects API on Kubernetes (#180)
* Added Ansible configuration to deploy the Objects API on single server (#59)

**Documentation**

* Added a tutorial how to use the Objects API and the Objecttypes API with examples (#61)
* Documented how to configure authentication and authorization for the Objects API and the Objecttypes API (#179)
* Documented deployment of the Objects API and the Objecttypes API on single server and Kubernetes (#59)
* Translated descriptions for `Content-Crs` and `Accept-Crs` headers from Dutch to English in the OAS (#106)
* Added information about validation to the OAS (#106)


1.0.0 (2021-01-13)
------------------

🎉 First release of Objects API.
