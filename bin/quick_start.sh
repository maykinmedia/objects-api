#!/bin/sh

set -ex

wget https://raw.githubusercontent.com/maykinmedia/objects-api/master/docker-compose-quickstart.yml -O docker-compose-qs.yml
docker-compose -f docker-compose-qs.yml up -d
docker-compose exec -T web src/manage.py loaddata demodata
