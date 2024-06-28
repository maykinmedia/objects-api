#!/bin/bash
#
# Dump the current OAS into YAML file src/openapi.yml
#
# Run this script from the root of the repository

if [ "$1" = "" ]; then
    echo "You need to pass a version in the first argument"
    exit 1
fi

if [ "$1" != "v1" ] && [ "$1" != "v2" ]; then
    echo "You need to pass a correct version in the first argument. Available values: v1, v2"
    exit 1
fi

export SCHEMA_PATH=src/objects/api/$1/openapi.yaml

OUTPUT_FILE=$2

src/manage.py spectacular --file ${OUTPUT_FILE:-$SCHEMA_PATH} --validate --api-version $1
