#!/bin/bash
#
# Dump the current (local database) admin layout to a JSON fixture. This
# overwrites the existing one.
#
# You can load this fixture with:
# $ src/manage.py loaddata demodata
#
# Run this script from the root of the repository

src/manage.py dumpdata --indent=4 --natural-foreign --natural-primary core accounts.objectpermission zgw_consumers.service > src/objects/fixtures/demodata.json
