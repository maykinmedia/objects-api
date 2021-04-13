.. _api_authorization:

=============
Authorization
=============

While :ref:`api_authentication` is a process of verifying who a client is, authorization
is the process of verifying what they have access to. Authorization is usually
done after successful authentication.

Objecttypes API
===============

The Objecttypes API doesn't have a particular authorization model, i.e. every
authenticated client has access to all object types.

Objects API
===========

In the Objects API, clients have explicit access to objects based on their
object types. Permissions for particular object types can be configured in the
admin. In the example below we will create a permission to modify tree objects, i.e.
objects of "Boom" object type.

Access to Objecttypes API
-------------------------
Since the access to objects is based on their object types, the Objects API should have
credentials to communicate with the Objecttypes API.

.. image:: _assets/img/authorization_objects_main_service.png
    :alt: Click on the "add" button for "Services"

In the admin page of the Objects API click on the "add" button for "Services"
resource.

.. image:: _assets/img/authorization_objects_service.png
    :alt: Fill in the form and click on "save" button

Fill in the form with the information about the Objecttypes API and put the Objecttypes API
created in the :ref:`api_authentication` section of this document into "Header value" field.
If you use NLX you can configure it in the "NLX url" field. After the form is submitted
the Objects API can access the Objecttypes API since it now has a security token for it.

Add an object type
------------------

Now we can add an object type to the Objects API, to define permissions.

.. image:: _assets/img/authorization_objects_main_objecttype.png
    :alt: Click on the "add" button for "Object type"

In the admin page of the Objects API click on the "add" button for "Object types"
resource.

.. image:: _assets/img/authorization_objects_objecttype.png
    :alt: Fill in the form and click on "save" button

Choose the service created in the previous step and fill in the uuid of the "Boom" object type.
After the form is submitted the object type name will be retrieved automatically from
the Objecttypes API.


Add a permission
----------------

Finally it's time to create a permission to access objects with "boom" object types.
Go to the token which should be granted this permission (it was probably created in the
:ref:`api_authentication` section of this document).

.. image:: _assets/img/authorization_objects_permissions.png
    :alt: Fill in the form and click on "save" button

In the "Permissions" section choose the object type created in the previous step and
choose the rights this token will have and submit the form.

Now the client who has this token can access the objects with the "Boom" object type.

If you want to know how to use Objects API you can follow :ref:`api_usage`
