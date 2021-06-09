#!/bin/bash
#
# Dump the current OAS into YAML file src/openapi.yml
#
# Run this script from the root of the repository

src/manage.py spectacular --file src/openapi.yaml --validate
