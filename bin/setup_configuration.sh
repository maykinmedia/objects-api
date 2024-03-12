#!/bin/bash

# setup initial configuration using environment variables
# Run this script from the root of the repository

#set -e
${SCRIPTPATH}/wait_for_db.sh

src/manage.py migrate
src/manage.py setup_configuration --no-selftest
