#!/bin/bash
#
# Dump the current OAS into YAML file src/openapi.yml
#
# Run this script from the root of the repository

if [ "$1" = "" ]; then
    echo "You need to pass a version in the first argument"
    exit 1
fi

if [ "$1" != "1" ]; then
    echo "You need to pass a correct version in the first argument. Available values: 1"
    exit 1
fi

export SCHEMA_PATH=src/objects/api/v$1/openapi.yaml

src/manage.py spectacular --file $SCHEMA_PATH --validate --api-version $1
