#!/bin/bash

# setup initial configuration using a yaml file
# Run this script from the root of the repository

set -e
echo "ENTRATO"
if [[ "${RUN_SETUP_CONFIG,,}" =~ ^(true|1|yes)$ ]]; then
    echo "ENTRATO 1"
    # wait for required services
    /wait_for_db.sh
    
    src/manage.py migrate
    src/manage.py setup_configuration --yaml-file setup_configuration/data.yaml
    echo "USCITO 1"
fi
echo "USCITO "
