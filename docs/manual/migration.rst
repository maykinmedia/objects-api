.. _objecttype_migration:

ObjectType API migration
========================

In 4.0.0 the ObjectTypes API will be merged into the Objects API so that only one application is needed.

Importing objecttype data
-------------------------
Before updating to 4.0.0 all objecttypes need to be imported. This can be done with the `import_objecttypes` command.
This command will fetch all objecttypes and their versions from an objecttype service based on its identifier/slug
and update existing objecttypes or create new ones if they have not been added to the objecttypes API.

Please note that after the update the objecttypes API is still being used in Objects API <4.0.0 the command only fetches the data.
From 4.0.0 onwards it will use the imported objecttypes.
