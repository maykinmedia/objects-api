#!/bin/bash
#
# Dump the current OAS into YAML file src/openapi.yml
#
# Run this script from the root of the repository


export SCHEMA_PATH=src/objects/api/v2/openapi.yaml

OUTPUT_FILE=$1

src/manage.py spectacular --file ${OUTPUT_FILE:-$SCHEMA_PATH} --validate --lang="en"
